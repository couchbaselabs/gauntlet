```properties
Scope=inventory
Collection=flights
```

## **Document structure**
**Key** `Flight_id`
```json
{
  "flight_id": "AA001",
  "status": "active",
  "airline": "American Airlines",
  "model": "Boeing 737",
  "departure_date": "2012-04-23T18:25:43.511Z",
  "departing_airport": "AZ",
  "arriving_airport": "CA",
  "seats": [
    {
      "seatnumber": "1A",
      "available": true,
      "class": "economy",
      "price": 500
    },
    {
      "seatnumber": "1B",
      "available": true,
      "class": "economy",
      "price": 500
    },
    {
      "seatnumber": "1C",
      "available": true,
      "class": "economy",
      "price": 500
    },
    {
      "seatnumber": "2A",
      "available": false,
      "class": "economy",
      "price": 500
    }
  ]
}
```
