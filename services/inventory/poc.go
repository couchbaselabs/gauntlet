// main.go
package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"

	gocb "github.com/couchbase/gocb/v2"
	"github.com/gorilla/mux"
)

type Seat struct {
	seatnumber string
	available  string
	class      string
	price      string
}

// Flight
type Flight struct {
	FlightID         string `json:"flight_id"`
	Status           string `json:"status"`
	Airline          string `json:"airline"`
	Model            string `json:"model"`
	DepartureDate    string `json:"departure_date"`
	DepartingAirport string `json:"departing_airport"`
	ArrivingAirport  string `json:"arriving_airport"`
	Seats            []Seat `json:"seats"`
}

var CBCluster *gocb.Cluster
var E2EBucket *gocb.Bucket
var InventoryScope *gocb.Scope
var FlightsCollection *gocb.Collection
var err error

func createNewFlight(w http.ResponseWriter, r *http.Request) {
	reqBody, _ := ioutil.ReadAll(r.Body)
	defer r.Body.Close()
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	var newflight Flight
	json.Unmarshal(reqBody, &newflight)
	
	flightId := fmt.Sprintf("%s%d", "AA", rand.Intn(100))
	newflight.FlightID = flightId
	_, err = FlightsCollection.Upsert(flightId, newflight, nil)
	if err != nil {
		log.Fatal(err)
	}
	// Get the document back
	getResult, err := FlightsCollection.Get(flightId, nil)
	if err != nil {
		log.Fatal(err)
	}

	var f interface{}
	if err := getResult.Content(&f); err != nil {
		panic(err)
	}
	json.NewEncoder(w).Encode(f)
}
func getFlightById(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Endpoint Hit: flight")
	vars := mux.Vars(r)
	key := vars["flight_id"]

	getResult, err := FlightsCollection.Get(key, &gocb.GetOptions{})
	if err != nil {
		panic(err)
	}
	var myFlight interface{}
	if err := getResult.Content(&myFlight); err != nil {
		panic(err)
	}
	fmt.Println(myFlight)
	json.NewEncoder(w).Encode(myFlight)
}
func getAllFlights(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Endpoint Hit: flights")
	vars := mux.Vars(r)
	airlineParam := vars["airline"]
	fmt.Println(airlineParam)
	// Perform a N1QL Query
	query := fmt.Sprintf("SELECT * FROM `e2e`.inventory.flights WHERE airline='%s' LIMIT 10;", airlineParam)
	fmt.Println(query)
	queryResult, err := CBCluster.Query(query, &gocb.QueryOptions{})
	// check query was successful
	if err != nil {
		panic(err)
	}
	var Flights []interface{}
	// Print each found Row
	for queryResult.Next() {
		var result interface{}
		err := queryResult.Row(&result)
		if err != nil {
			panic(err)
		}
		fmt.Println(result)
		Flights = append(Flights, result)
	}

	if err := queryResult.Err(); err != nil {
		panic(err)
	}
	json.NewEncoder(w).Encode(Flights)
}
func handleRequests() {
	myRouter := mux.NewRouter().StrictSlash(true)
	myRouter.HandleFunc("/flights/{airline}", getAllFlights)
	myRouter.HandleFunc("/newflight", createNewFlight).Methods("POST")
	myRouter.HandleFunc("/flight/{flight_id}", getFlightById)

	log.Fatal(http.ListenAndServe(":10000", myRouter))
}

func main() {
	hostname := os.Getenv("DB_HOSTNAME")
	bucketName := "e2e"
	username := os.Getenv("CAPELLA_USERNAME")
	password := os.Getenv("CAPELLA_PASSWORD")

	// Initialize the connection
	cluster, err := gocb.Connect("couchbases://"+hostname+"?ssl=no_verify", gocb.ClusterOptions{
		Authenticator: gocb.PasswordAuthenticator{
			Username: username,
			Password: password,
		},
	})
	if err != nil {
		log.Fatal(err)
	}

    CBCluster = cluster
	bucket := cluster.Bucket(bucketName)
	err = bucket.WaitUntilReady(5*time.Second, nil)
	if err != nil {
		log.Fatal(err)
	}
	// Get a user-defined collection reference
	InventoryScope = bucket.Scope("inventory")
	FlightsCollection = InventoryScope.Collection("flights")

	cluster.QueryIndexes().CreatePrimaryIndex(bucketName, &gocb.CreatePrimaryQueryIndexOptions{
		IgnoreIfExists: true,
	})

	handleRequests()
}
