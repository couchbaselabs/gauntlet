package com.services.e2eapp.utilities;

import com.couchbase.client.java.json.JsonArray;
import com.couchbase.client.java.json.JsonObject;
import com.services.e2eapp.core.BookingService;

public class BookingUtilties {

    public static JsonObject rollbackTickets(JsonObject flightInfo, JsonArray ticketsToRollback){
        JsonArray totalSeatsInfo = flightInfo.getArray("seats");
        for ( Object eachSeatObject:totalSeatsInfo){
            JsonObject eachSeat = (JsonObject)eachSeatObject;

            if(ticketsToRollback.contains(eachSeat.getString("seatnumber")))
                eachSeat.put("available",true);
        }
        return flightInfo;
    }

}
