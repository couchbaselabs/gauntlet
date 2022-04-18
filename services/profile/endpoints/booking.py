import uuid

from flask_restful import Resource, reqparse


class UserAuth(Resource):
    def __init__(self, cb, commonutil):
        self.cb = cb
        self.commonutil = commonutil
        self.message = "Authenticating user"

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        # LDAP validation
        result = self.commonutil.ldap_util.authenticate(args["username"],
                                                        args['password'])
        if result:
            return {"Msg": "OK"}, 200
        return {"Msg": "Invalid credentials"}, 400


class CreateUser(Resource):
    def __init__(self, cb, commonutil):
        self.cb = cb
        self.commonutil = commonutil
        self.message = "creating user"

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('firstname', required=True)
        parser.add_argument('lastname', required=True)
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        # generate unique id
        passenger_id = uuid.uuid1()

        res = self.commonutil.ldap_util.create_user(args)
        if res is False:
            return {"Error": "LDAP User Creation failed"}, 400

        res = self.cb.add_user(args['firstname'], args['lastname'],
                               args['username'], args['password'],
                               str(passenger_id))
        if not res:
            return {"Error": "User Creation failed"}, 400

        return {"Msg": "User Created Successfully"}, 200


class DeleteUser(Resource):
    def __init__(self, cb, commonutil):
        self.cb = cb
        self.commonutil = commonutil
        self.message = "deleting user"

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('firstname', required=True)
        parser.add_argument('lastname', required=True)
        args = parser.parse_args()

        res = self.commonutil.ldap_util.delete_user(args)
        if res is False:
            return {"Error": "LDAP User Deletion failed"}, 400

        # Don't worry about the outcome since this can fail
        # if the user document is not present in the database
        self.cb.delete_user(args['firstname'], args['lastname'])

        return {"Msg": "User Deleted Successfully"}, 200


class ConfirmBooking(Resource):
    def __init__(self, cb, commonutil):
        self.cb = cb
        self.commonutil = commonutil
        self.message = "calling confirm Booking"

    def post(self):
        parser = reqparse.RequestParser()

        # Unique Identifier
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('flightSeats', required=True)
        parser.add_argument('bankAccount', required=True)
        parser.add_argument('flightId', required=True)
        parser.add_argument('bookingClass', required=True)
        args = parser.parse_args()

        res = self.cb.get_user(args['username'])
        print(res)
        if len(res) == 0:
            return {"Error": "Username does not exists"}, 400
        if args['password'] != res[0]['password']:
            return {"Error": "Password mismatch"}, 400

        res = self.cb.get_user_id(args["username"])
        pass_id = res[0]['id']

        body = {"flightSeats": int(args["flightSeats"]),
                "bankAccount": args["bankAccount"],
                "flightId": args["flightId"],
                "bookingClass": args["bookingClass"],
                "passengerId": pass_id}

        status, content, response = self.commonutil.http_request(
            service="booking", uri="confirmBooking",
            method="POST", body=body)
        if status:
            self.cb.update_user(args["username"], content["id"])
            return {"Msg": content}, 200
        else:
            return {"Error": content}, 400


class EditBooking(Resource):
    def __init__(self, cb, commonutil):
        self.cb = cb
        self.commonutil = commonutil
        self.message = "calling confirm Booking"

    def post(self):
        parser = reqparse.RequestParser()

        # Unique Identifier
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('flightSeats')
        parser.add_argument('hotelRooms')
        parser.add_argument('bankAccount')
        parser.add_argument('flightName')
        parser.add_argument('schedule')
        parser.add_argument('booking_id')
        args = parser.parse_args()

        res = self.cb.get_user(args['username'])
        print(res)
        if len(res) == 0:
            return {"Error": "Username does not exists"}, 400
        if args['password'] != res[0]['password']:
            return {"Error": "Password mismatch"}, 400

        res = self.cb.get_all_bookings(args['username'])
        all_bookings = res[0]["bookings"]
        if args["booking_id"] not in all_bookings:
            return {"Error": "booking_id does not belongs to this user"}, 400

        body = {"booking_id": args["booking_id"]}
        if "flightSeats" in args.keys():
            body["flightSeats"] = args["flightSeats"]
        if "hotelRooms" in args.keys():
            body["hotelRooms"] = args["hotelRooms"]
        if "bankAccount" in args.keys():
            body["bankAccount"] = args["bankAccount"]
        if "flightName" in args.keys():
            body["flightName"] = args["flightName"]
        if "schedule" in args.keys():
            body["schedule"] = args["schedule"]

        status, content, response = self.commonutil.http_request(
            service="booking", uri="editBooking", method="PUT", body=body)
        if status:
            return {"Msg": content}, 200
        else:
            return {"Error": content}, 400


class AllBookings(Resource):
    def __init__(self, cb, commonutil):
        self.cb = cb
        self.commonutil = commonutil

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        res = self.cb.get_user(args['username'])
        print(res)
        if len(res) == 0:
            return {"Error": "Username does not exists"}, 400
        if args['password'] != res[0]['password']:
            return {"Error": "Password mismatch"}, 400

        res = self.cb.get_all_bookings(args['username'])
        print(res)
        return {"Msg": res}, 200


class GetBooking(Resource):
    def __init__(self, cb, commonutil):
        self.cb = cb
        self.commonutil = commonutil

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)

        parser.add_argument('id', required=True)
        args = parser.parse_args()

        res = self.cb.get_user(args['username'])
        print(res)
        if len(res) == 0:
            return {"Error": "Username does not exists"}, 400
        if args['password'] != res[0]['password']:
            return {"Error": "Password mismatch"}, 400

        res = self.cb.get_all_bookings(args['username'])
        all_bookings = res[0]["bookings"]
        if args["id"] not in all_bookings:
            return {"Error": "id does not belongs to this user"}, 400

        body = {"id":  args["id"]}
        status, content, response = self.commonutil.http_request(
            service="booking", uri="getBooking", method="GET", body=body)
        if status:
            return {"Msg": content}, 200
        else:
            return {"Error": content}, 400


class CancelBooking(Resource):
    def __init__(self, cb, commonutil):
        self.cb = cb
        self.commonutil = commonutil

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('id', required=True)
        args = parser.parse_args()

        res = self.cb.get_user(args['username'])
        print(res)
        if len(res) == 0:
            return {"Error": "Username does not exists"}, 400
        if args['password'] != res[0]['password']:
            return {"Error": "Password mismatch"}, 400

        res = self.cb.get_all_bookings(args['username'])
        all_bookings = res[0]["bookings"]
        if args["id"] not in all_bookings:
            return {"Error": "id does not belongs to this user"}, 400

        body = {"id": args["id"]}

        status, content, response = self.commonutil.http_request(
            service="booking", uri="cancelBooking",
            method="DELETE", body=body)
        if status:
            return {"Msg": content}, 200
        else:
            return {"Error": content}, 400
