package main

import (
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"
)

func handler(w http.ResponseWriter, r *http.Request) {
	timeWaitStr := r.URL.Query().Get("sleep_milliseconds")
	if len(timeWaitStr) != 0 {
		timeWait, err := strconv.Atoi(timeWaitStr)
		if err != nil {
			fmt.Println("wrong int")
		} else {
			fmt.Println("waining for milliseconds", timeWait)
			time.Sleep(time.Duration(timeWait) * time.Millisecond)
		}
	}
	fmt.Fprintf(w, `{"result": "ok"}`)
}

func main() {
	fmt.Println("listening at http://localhost:8888/?sleep_milliseconds=20")
	http.HandleFunc("/", handler)
	log.Fatal(http.ListenAndServe(":8888", nil))
}
