# vegeta

## install
`$ go get -u github.com/tsenart/vegeta`

## simple usage
`echo 'GET http://localhost:8890/_info' | vegeta -cpus 1 attack -rate 100 -duration 10s -timeout 1s | vegeta report -reporter json | jq`

`echo 'GET http://localhost:8890/_info' | vegeta -cpus 1 attack -rate 100 -duration 4s -timeout 1s | vegeta report -reporter plot > plot.html`

`echo 'GET http://localhost:8890/sleep50' | vegeta -cpus 1 attack -rate 100 -duration 4s -timeout 1s | vegeta report -reporter plot > /tmp/plot.html; open /tmp/plot.html