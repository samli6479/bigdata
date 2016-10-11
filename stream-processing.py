# 1. read from kafka, kafka broker, kafka topic
# 2. write back to kafka, kafka broker, new kafka topic

import sys
import atexit
import logging
import json

from kafka import KafkaProducer
from kafka.errors import kafkaError, kafkaTimeoutError
from pyspark import SparkContext # how to talk to spark
from pyspark.streaming import SteamingContext
from pyspark.streaming.kafka import KafkaUtils

logger_format = "%(asctime)-15s %(message)s"
logging.basicConfig(format=logger_format)
logger = logging.getLogger('stream-processing')
logger.setLevel(logging.INFO)

topic = ""
new_topic = ""
kafka_broker = ""
kafka_producer = ""

def shutdown_hook(producer):
	try:
		logger.info('flush pending messages to kafka')
		producer.flush(10)
		logger.info('finish flushing pending messages')
	except kafkaError as kafka_error:
		logger.warn('Failed to flush pending messages to kafka')
	finally:
		try:
			producer.close(10)
		except Exception as e:
			logger.warn('Failed to clode kafka connection')

def prodcess(timeobj, rdd):
	# - calculate the average
	num_of_records = rdd.count()
	if num_of_records == 0:
		return
	price_sum = rdd.map(lambda record: float(json.loads(record[1].decode('utf-8'))[0].get('LastTradePrice'))).reduce(lambda a, b: a+b)
	average = price_sum/num_of_records
	logger.info('Received %d records from Kafka, average price is %f' % (num_of_records, average))

	# - write back to kafka
	# {timestamp, average}
	data = json.dumps({
		'timestamp': time.time(),
		'average': average
		})
	kafka_producer.send(new_topic, value = data)





if __name__ == "__main__":
	# kafka broker, topic,new topic and application name
	if len(sys.argv) != 4:
		print('Usage: stream-processing [topic] [new topic] [kafka-broker]')
		exit(1)

	topic, new_topic, kafka_broker = sys.argv[1:]

	# -setup connection to spark cluster
	# local[x] -x number of cores
	sc = SparkContext("local[2]", "StockAveragePrice")
	# sc.setLogLevel('ERROR')
	# Streaming(sc,x)  - open in x seconds 
	ssc = StreamingContext(sc, 5)

	# - create a data stream from spark
	# we can add pur own kafka consumer to process but not recommanded
	# due to additional layer
	directKafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {'metadata.broker.list':kafka_broker})

	# - for each RDD, do something
	# Action
	directKafkaStream.foreachRDD(process)

	# - instantiate kafka producer
	kafka_producer = KafkaProducer(bootstrap_servers=kafka_broker)

	# - setup proper shutdown hook
	# Action
	atexit.register(shutdown_hook, kafka_producer)

	ssc.start()
	ssc.awaitTermination()