package com.services.e2eapp.core;

import com.couchbase.client.core.deps.io.netty.handler.ssl.util.InsecureTrustManagerFactory;
import com.couchbase.client.core.env.IoConfig;
import com.couchbase.client.core.env.SecurityConfig;
import com.couchbase.client.java.Bucket;
import com.couchbase.client.java.Cluster;
import com.couchbase.client.java.ClusterOptions;
import com.couchbase.client.java.Collection;
import com.couchbase.client.java.env.ClusterEnvironment;
import com.couchbase.client.java.json.JsonArray;
import com.couchbase.client.java.json.JsonObject;
import com.couchbase.transactions.TransactionDurabilityLevel;
import com.couchbase.transactions.TransactionGetResult;
import com.couchbase.transactions.Transactions;
import com.couchbase.transactions.config.TransactionConfigBuilder;
import com.j256.ormlite.logger.Logger;
import com.services.e2eapp.logging.LogUtil;
import com.services.e2eapp.utilities.BookingUtilties;
import reactor.util.annotation.Nullable;
import reactor.util.function.Tuple2;
import reactor.util.function.Tuples;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicReference;

import static com.services.e2eapp.constants.Constants.*;


enum BookingStatus { SUCCESS, FAIL}
public class BookingService {
    private final int flightTicketCost =100;

    private static final Logger logger = LogUtil.getLogger(BookingService.class);
    /*private final String CB_SERVER_HOST = System.getenv("DB_HOSTNAME");
    private final String CB_ADMIN_USER = System.getenv("CAPELLA_USERNAME");
    private final String CB_ADMIN_PASSWORD = System.getenv("CAPELLA_PASSWORD");*/

    private final String CB_SERVER_HOST = "cb.wdffruwj0habuyu.cloud.couchbase.com";
    private final String CB_ADMIN_USER = "admin";
    private final String CB_ADMIN_PASSWORD = "1@Password";

    private String bookingId="";
    private String flightId="";
    private int flightSeats;
    private String bookingClass ="";
    private String bankAccount="";
    private int hotelRooms;
    private String comments="";

    private Cluster cluster;
    private Bucket bucket;

    private Collection inventoryScope_flightsCollection;
    private Collection bookingScope_flightsCollection;
    private Collection profileScope_walletCollection;

    private  Transactions transactions;

    public BookingService(String bookingId){
        this.bookingId = bookingId;
        ClusterEnvironment env = ClusterEnvironment.builder()
            .securityConfig(SecurityConfig.enableTls(true)
                .trustManagerFactory(InsecureTrustManagerFactory.INSTANCE))
            .ioConfig(IoConfig.enableDnsSrv(true))
            .build();

        // Initialize the Connection

        cluster = Cluster.connect(CB_SERVER_HOST,
            ClusterOptions.clusterOptions(CB_ADMIN_USER, CB_ADMIN_PASSWORD).environment(env));

         bucket = cluster.bucket(BUCKET_NAME);
         bucket.waitUntilReady(Duration.parse("PT10S"));

         inventoryScope_flightsCollection = bucket.scope(INVENTORY_SCOPE).collection(FLIGHTS_COLLECTION_NAME);
         bookingScope_flightsCollection = bucket.scope(BOOKING_SCOPE).collection(FLIGHTS_COLLECTION_NAME);
         profileScope_walletCollection = bucket.scope(PROFILES_SCOPE).collection(WALLET_COLLECTION_NAME);

         TransactionConfigBuilder builder = TransactionConfigBuilder.create()
                .durabilityLevel(TransactionDurabilityLevel.MAJORITY)
                .expirationTime(Duration.ofSeconds(60))
                .cleanupWindow(Duration.ofSeconds(10));
        transactions = Transactions.create(cluster, builder);

        waitUntilReady();
    }

    private void waitUntilReady(){
        cluster.bucket(BUCKET_NAME).waitUntilReady(Duration.ofSeconds(10));
    }

    public BookingService flightId(String flightId){
        this.flightId = flightId;
        return this;
    }

    public BookingService flightSeats(int flightSeats){
        this.flightSeats = flightSeats;
        return this;
    }

    public BookingService bookingClass(String bookingClass){
        this.bookingClass = bookingClass;
        return this;
    }

    public BookingService bankAccount(String bankAccount){
        this.bankAccount = bankAccount;
        return this;
    }

    public BookingService hotelRooms(int hotelRooms){
        this.hotelRooms = hotelRooms;
        return this;
    }


    private void comments(String comments){
        this.comments = comments;
    }

    public String confirmBooking(){
        AtomicReference<JsonObject> booking = new AtomicReference<JsonObject>();
        try{
            transactions.run((ctx) -> {
                TransactionGetResult initialFlightInventory  = ctx.get(inventoryScope_flightsCollection,flightId);
                Tuple2<JsonObject, JsonArray> bookingDetails = bookandSeatingDetails(initialFlightInventory.contentAsObject(),flightSeats);
                JsonObject updatedFlightInventory = bookingDetails.getT1();
                ctx.replace(initialFlightInventory,updatedFlightInventory);

                //Update booking information
                JsonArray seatsBooked = bookingDetails.getT2();
                int totalCost = flightSeats*flightTicketCost;
                JsonObject bookingInformation = getNewBookingObject(seatsBooked, BookingStatus.SUCCESS,totalCost,null);
                ctx.insert(bookingScope_flightsCollection,bookingId, bookingInformation);
                booking.set(bookingInformation);

                //Update wallet information
                TransactionGetResult initialBankAccountInfo  = ctx.get(profileScope_walletCollection,bankAccount);
                JsonObject bankAccountObject = initialBankAccountInfo.contentAsObject();

                int currentBalance =bankAccountObject.getInt("wallet_balance");
                int finalBalance = currentBalance - totalCost;
                bankAccountObject.put("wallet_balance",finalBalance);

                ctx.replace(initialBankAccountInfo,bankAccountObject);
            });
            transactions.close();
        }catch(RuntimeException ex){
            JsonObject bookingInformation = getNewBookingObject(null, BookingStatus.FAIL,0,ex.getMessage());
            bookingScope_flightsCollection.insert(bookingId,bookingInformation);
            booking.set(bookingInformation);
        }
        return booking.get().toString();
    }

    public String getBooking(){
        AtomicReference<JsonObject> bookingDetails = new AtomicReference<>();
        transactions.run((ctx) -> {
            TransactionGetResult getResult = ctx.get(bookingScope_flightsCollection,bookingId);
            bookingDetails.set(getResult.contentAsObject());
        });
        return bookingDetails.get().toString();
    }

    public String editBooking(){
        AtomicReference<JsonObject> booking = new AtomicReference<JsonObject>();
        if(bookingScope_flightsCollection.get(bookingId).contentAsObject().getString("status").equals("Booking Cancelled")){
           return  "Cannot edit a cancelled booking";
        }

        transactions.run((ctx) -> {
            //Get previous booking details
            TransactionGetResult bookingInfoResult  = ctx.get(bookingScope_flightsCollection,bookingId);
            JsonObject bookingInfo = bookingInfoResult.contentAsObject();

            flightId(bookingInfo.getString("flightId"));
            bookingClass(bookingInfo.getString("bookingClass"));
            bankAccount(bookingInfo.getString("bankAccount"));
            JsonArray bookedTickets  = bookingInfo.getArray("TicketsBooked");
            int initialFlightsSeats= bookingInfo.getInt("flightSeats");

            //Update flight information
            TransactionGetResult originalFlightInventory  = ctx.get(inventoryScope_flightsCollection,flightId);
            JsonObject flightInfo = originalFlightInventory.contentAsObject();
            JsonObject updatedFlightInventory;
            int additionalTicketsToBook = flightSeats - initialFlightsSeats;

            if(additionalTicketsToBook > 0){
                //case where we need to add new tickets
                Tuple2<JsonObject, JsonArray> bookingDetails = bookandSeatingDetails(flightInfo,additionalTicketsToBook);
                updatedFlightInventory = bookingDetails.getT1();
                JsonArray newlyBookedTickets= bookingDetails.getT2();
                for (int i= 0; i<newlyBookedTickets.size();i++){
                    bookedTickets =  bookedTickets.add(newlyBookedTickets.get(i));
                }
            }else{
                //case where we need to remove existing tickets
                JsonArray rollbackTickets = JsonArray.create();
                JsonArray finalSetTickets = JsonArray.create();

                int ticketsToRemove = -1 * additionalTicketsToBook;
                for(int i =0; i< ticketsToRemove;i++){
                    rollbackTickets.add(bookedTickets.get(i));
                }
                for(int i =ticketsToRemove;i<bookedTickets.size();i++){
                    finalSetTickets.add(bookedTickets.get(i));
                }

                bookedTickets = finalSetTickets;
                updatedFlightInventory = BookingUtilties.rollbackTickets(flightInfo,rollbackTickets);
            }

            ctx.replace(originalFlightInventory,updatedFlightInventory);

            //update booking information
            int totalCost = flightSeats * flightTicketCost;
            bookingInfo.put("ticket_cost", totalCost);
            bookingInfo.put("flightSeats", flightSeats);
            bookingInfo.put("TicketsBooked", bookedTickets);
            booking.set(bookingInfo);
            ctx.replace(bookingInfoResult,bookingInfo);


            //Update wallet information
            TransactionGetResult initialBankAccountInfo  = ctx.get(profileScope_walletCollection,bankAccount);

            JsonObject bankAccountObject = initialBankAccountInfo.contentAsObject();
            int currentBalance =bankAccountObject.getInt("wallet_balance");
            int finalBalance = currentBalance - (additionalTicketsToBook * flightTicketCost);
            bankAccountObject.put("wallet_balance",finalBalance);

            ctx.replace(initialBankAccountInfo,bankAccountObject);
        });
        return booking.get().toString();
    }

    public String cancelBooking(){
        AtomicReference<JsonObject> booking = new AtomicReference<JsonObject>();

        transactions.run((ctx) -> {
            TransactionGetResult bookingInfoResult  = ctx.get(bookingScope_flightsCollection,bookingId);
            JsonObject bookingInfo = bookingInfoResult.contentAsObject();

            flightId(bookingInfo.getString("flightId"));
            bookingClass(bookingInfo.getString("bookingClass"));
            bankAccount(bookingInfo.getString("bankAccount"));

            //Update flight information
            TransactionGetResult originalFlightInventory  = ctx.get(inventoryScope_flightsCollection,flightId);
            JsonObject updatedFlightInfo = BookingUtilties.rollbackTickets(originalFlightInventory.contentAsObject(),bookingInfo.getArray("TicketsBooked"));
            ctx.replace(originalFlightInventory,updatedFlightInfo);


            //update booking information
            bookingInfo.put("status", "Booking Cancelled");
            booking.set(bookingInfo);
            ctx.replace(bookingInfoResult,bookingInfo);

            //Update wallet information
            TransactionGetResult initialBankAccountInfo  = ctx.get(profileScope_walletCollection,bankAccount);

            JsonObject bankAccountObject = initialBankAccountInfo.contentAsObject();
            int currentBalance =bankAccountObject.getInt("wallet_balance");
            int finalBalance = currentBalance + (flightSeats * flightTicketCost);
            bankAccountObject.put("wallet_balance",finalBalance);

            ctx.replace(initialBankAccountInfo,bankAccountObject);
        });
        return booking.get().toString();
    }

    /**
     * Updates and sends the flight inventory object. This is used in transaction replace to update the flights inventory in database
     * @param flightInventoryObject
     * @param seatsToBook
     * @return  Tuple of below two objects
     * 1. Updated flight inventory object
     * 2. Array of seats which are booked
     */
    private Tuple2<JsonObject, JsonArray> bookandSeatingDetails(JsonObject flightInventoryObject, int seatsToBook){
        JsonArray totalSeatsInfo = flightInventoryObject.getArray("seats");
        JsonArray seatsBooked =  JsonArray.create();
        for ( Object eachSeatInfo:totalSeatsInfo){
            if(seatsToBook>0){
                JsonObject eachSeat = (JsonObject)eachSeatInfo;
                if(eachSeat.getBoolean("available")){
                    eachSeat.put("available",false);
                    seatsBooked.add(eachSeat.getString("seatnumber"));
                    seatsToBook--;
                    logger.info("Booked one Ticket. Tickets left for booking:"+seatsToBook );
                }
            }else{
                logger.info("Completed booking all required tickets" );
                break;
            }
        }
        if(seatsToBook>0){
            throw new RuntimeException("Required seats are not available in this flight");
        }
        return Tuples.of(flightInventoryObject,seatsBooked);
    }

    public  JsonObject getNewBookingObject(JsonArray bookedTickets, BookingStatus bookingstatus, int totalCost , @Nullable String comments){
        JsonObject bookingObject = JsonObject.create()
                .put("id", bookingId)
                .put("totalCost",totalCost)
                .put("flightId", flightId)
                .put("flightSeats",flightSeats )
                .put("bookingClass", bookingClass)
                .put("bankAccount", bankAccount)
                .put("hotelRooms", hotelRooms);

        if(bookingstatus== BookingStatus.FAIL){
            bookingObject.put("status", "Booking Failed")
                            .put("Booking failure reason", comments);
        }

        if(bookingstatus== BookingStatus.SUCCESS){
            bookingObject.put("status", "Booking Confirmed")
                        .put("TicketsBooked", bookedTickets);
        }

        return bookingObject;
    }


}

