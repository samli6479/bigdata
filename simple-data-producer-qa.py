#!/usr/bin/env python

from kafka import KafkaConsumer

Consumer = KafkaConsumer('stock-analyzer',bootstrap_servers = '192.168.99.100:9092')

for msg in Consumer:
    print(msg)
