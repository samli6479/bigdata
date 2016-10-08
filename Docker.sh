#!/bin/bash

pyenv local 2.7.10

docker-machine start bigdata

docker start zookeeper

docker start kafka

docker start cassandra

docker start redis
