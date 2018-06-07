#!/bin/bash

locust -f dummy.py --master --master-bind-host=127.0.0.1 --master-bind-port=5557 --csv=foobar --no-web -c $1 -r $1 -n 1000 &
sleep 0.5
./a.out --url=http://127.0.0.1:8890/sleep50 --master-port=5557 --rpc=zeromq --max-rps $3 &
sleep $2
kill $(jobs -p)
exit 0
