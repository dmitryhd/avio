# Avio

aiohttp based microservice boilerplate

_Work in progress_

# Backlog
## v0.1
- [x] application
- [x] json request handlers
- [x] test setup
- [x] app runner
- [x] valid 404, 500, catch other errors
## v0.2
- [x] configuration file 
- [x] configuration from ENV
## v0.3
- [ ] statsd
- [x] measure handler time
- [ ] raven
- [ ] json logger
## v0.4
- [ ] Modularized application builder
- [ ] performance benchmark vs tornado
## v0.4
- [ ] periodic task to update (https://aiohttp.readthedocs.io/en/stable/web_advanced.html#background-tasks1)
- [ ] redis client
- [ ] handler time metrics by error codes
## v0.5
- [ ] mongodb adapter
- [ ] sphinx adapter
## v0.6
- [ ] microservice clients
- [ ] jsonschema validation
## opt
- [x] benchmark
- [ ] benchmark vs tornado
- [ ] uvloop
- [ ] ujson

### Benchmark
```
wrk -t1 -c10 -d10s -R 2000 -s benchmark/echo.lua http://127.0.0.1:8890/_echo
Running 10s test @ http://127.0.0.1:8890/_echo
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.13ms    1.90ms  11.32ms   73.87%
    Req/Sec       -nan      -nan   0.00      0.00%
  19943 requests in 10.00s, 4.53MB read
Requests/sec:   1994.33
Transfer/sec:    463.52KB
```

### Checklist

- application available everywhere
- raven and statsd responses limited
- graceful shutdown

