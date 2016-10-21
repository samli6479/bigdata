#!/bin/bash
gnome-terminal -e 'python simple-data-producer.py AAPL stock-analyzer 192.168.99.100:9092'
gnome-terminal -e 'python data-storage.py stock-analyzer 192.168.99.100:9092 stock stock 192.168.99.100'
# change the name to your directory
gnome-terminal -e 'cd /home/name/spark/bin/spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.0.0.jar stream-processing.py stock-analyzer average-stock-price 192.168.99.100:9092'
gnome-terminal -e 'python redis-publisher.py average-stock-price 192.168.99.100:9092 average-stock-price 192.168.99.100 6379'
gnome-terminal -e 'cd ./nodejs/;node index.js --port=3000 --redis_host=192.168.99.100 --redis_port=6379 --channel=average-stock-price'
