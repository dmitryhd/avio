wrk.method = "POST"
wrk.body   = '{"jsonrpc":"2.0","method":"cita_sendTransaction","params":["abcd"],"id":2}'
wrk.headers["Content-Type"] = "application/json"
