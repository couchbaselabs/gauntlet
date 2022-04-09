package com.services.e2eapp.endpoints;

import com.services.e2eapp.core.BookingService;
import com.services.e2eapp.jsonobjects.BookingId;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

@RestController
public class BookingEndpoints {
    @PostMapping("/confirmBooking")
    public String confirmBooking(@RequestBody Map<String, ?> input) {
        return new BookingService(getRandomId())
                .flightId((String) input.get("flightId"))
                .flightSeats(((Integer)input.get("flightSeats")).intValue())
                .bookingClass((String) input.get("bookingClass"))
                .bankAccount((String) input.get("bankAccount"))
                .confirmBooking();
    }

    @GetMapping("/getBooking")
    public String getBooking(@RequestBody BookingId bookingId) {
        return new BookingService(bookingId.getId())
                .getBooking();
    }

    @PutMapping("/editBooking")
    public String editBooking(@RequestBody Map<String, ?> input) {
        return new BookingService((String) input.get("id"))
                .flightSeats(((Integer)input.get("flightSeats")).intValue())
                .editBooking();
    }

    @DeleteMapping("/cancelBooking")
    public String cancelBooking(@RequestBody BookingId bookingId) {
        return new BookingService(bookingId.getId())
                .cancelBooking();
    }

    private String getRandomId(){
       return UUID.randomUUID().toString();
    }
}
