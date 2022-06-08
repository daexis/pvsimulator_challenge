#!/bin/sh
cd ./data/log
rm -rf *.log *.csv *.png *.tmp
cd ../rabbitmq
rm -R mnesia
rm -rf .erlang.cookie
echo "Cleaned"