dependencies: Use this repo for all dependencies and reusable code. 
		1. Any resources eg: config files, json files etc
		2. Please ensure to add the code here ,if other team members are re-using the code

clients: Rest Api's repository

gateway: API Gateway repo

services: Code repo for Microservices. We might have split based on languages implementation

management: common interfaces , notifications etc are handled here

Data: CB server info is stored.

Inventory Service endpoints:
----------------------------
Create Flight: 

	curl -X POST http://localhost:10000/newflight 
	-d '{"airline":"American Airlines",
	"arriving_airport":"CA",
	"departing_airport":"AZ",
	"departure_date":"2012-04-23T18:25:43.511Z",
	"model":"Boeing 737",
	"seats":[
	{"available":true,"class":"economy","price":500,"seatnumber":"1A"},
	{"available":true,"class":"economy","price":500,"seatnumber":"1B"}],
	"status":"active"}'

Get all flights by airline: 

	curl -X GET http://localhost:10000/flights/American%20Airlines

Get flight by flight ID: 

	curl -X GET http://localhost:10000/flight/AA001

Profile Service endpoints:
----------------------------

createUser:

    curl -X POST http://localhost:5000/createUser -d '{"username":"username", "password": "password",
    "firstname":"firstname", "lastname":"lastname"}'

confirmBooking:

    curl -X POST http://localhost:5000/confirmBooking -d '{"username":"username", "password": "password",
    "flightSeats":"flightSeats", "hotelRooms":"hotelRooms", "bankAccount": "bankAccount", "flightId": "flightId", "schedule":"schedule"}'

EditBooking:

    curl -X POST http://localhost:5000/editBooking -d '{"username":"username", "password": "password",
    "flightSeats":"flightSeats", "hotelRooms":"hotelRooms", "bankAccount": "bankAccount", "flightId": "flightId",
    "schedule":"schedule", "booking_id": "booking_id"}'

Get all bookings by user:

    curl -X POST http://localhost:5000/allBookings -d '{"username":"username", "password": "password"}'

Get details of booking of a user

    curl -X POST http://localhost:5000/getBooking -d '{"username":"username", "password": "password", "booking_id": "booking_id"}'

CancelBooking

    curl -X POST http://localhost:5000/cancelBooking -d '{"username":"username", "password": "password", "booking_id": "booking_id"}'

 
 
 Booking Service endpoints:
 ----------------------------
 confirmBooking: Performs an actual reservation of flights and charges the customer
 
     curl --location --request POST 'localhost:8082/confirmBooking?flightSeats=3&flightId=AA001_08172021&bankAccount=123456&bookingClass=business&passengerId=1234'
 
 
 Get a Booking: Get info on a particular booking Id
 
     curl --location --request GET '172.23.122.118:8082/getBooking?id=9e0eb2aa-76fe-4577-a731-bbaf2025b717'

 EditBooking: Modifies an existing reservation
 
     curl --location --request PUT '172.23.122.118:8082/editBooking?newFlightSeats=1&id=9e0eb2aa-76fe-4577-a731-bbaf2025b717'


CancelBooking: Cancels an existing reservation

    curl --location --request DELETE '172.23.122.118:8082/cancelBooking?id=9e0eb2aa-76fe-4577-a731-bbaf2025b717'
 
