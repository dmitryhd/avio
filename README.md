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
- [x] measure handler time
- [x] http clients
- [x] dump stub get json responses
- [x] test handler (several responses)
- [x] jupyter autobenchmark
- [x] reliable benchmark 
- [x] check locustio
## v0.4
- [x] statsd
- [ ] json logger
- [ ] raven
- [ ] handler time metrics by error codes
- [ ] default values at config
## v0.5
- [ ] run benchmark at macos
- [ ] pyflame profile
- [ ] smart stub (delay, errors, json responses, bursts)
- [ ] performance benchmark vs tornado
- [ ] periodic task to update (https://aiohttp.readthedocs.io/en/stable/web_advanced.html#background-tasks1)
- [ ] redis client
- [ ] readiness/liveliness probe
- [ ] swagger autodoc
## v0.6
- [ ] jsonschema validation
- [ ] mongodb adapter
- [ ] sphinx adapter
## v0.7
- [ ] Modularized application builder
- [ ] 

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

