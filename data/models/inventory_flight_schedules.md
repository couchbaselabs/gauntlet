```properties
Scope=inventory
Collection=flight_schedules
```

## **Document structure**
**Key** `flightNum_MMDDYYYY`
```json
{
  "departing_airport": "AZ",
  "arriving_airport": "CA",
  "departure_date": "2012-04-23T18:25:43.511Z",
  "model": "Boeing 737",
  "airline": "American Airlines",
  "seats": [
    {
      "available": true,
      "seatnumber": "1A",
      "class": "business",
      "price": 100
    },
    {
      "available": false,
      "seatnumber": "1B",
      "class": "business",
      "price": 100
    },
    {
      "available": false,
      "seatnumber": "1C",
      "class": "business",
      "price": 100
    },
    {
      "available": true,
      "seatnumber": "2A",
      "class": "business",
      "price": 100
    }
  ],
  "flight_id": "AA001_08162021",
  "status": "active"
}
```
