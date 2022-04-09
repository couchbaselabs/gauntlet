import click

from tabulate import tabulate

from constants.app import E2EApp
from constants.profiles import Profiles
from lib.common import auth_options, common_options, read_config_yaml
from lib.rest_helper import RestAPI


@click.group()
def profile():
    pass


@profile.command()
@auth_options
@click.option('--first_name', '-f', default=None,
              help='First name of the user')
@click.option('--last_name', '-l',  default=None,
              help='Last name of the user')
def create_user(username, password, first_name, last_name):
    if first_name is None:
        first_name = input("First name: ")
    if last_name is None:
        last_name = input("Last name: ")
    if username is None:
        username = input("Username: ")
    if password is None:
        password = input("Password: ")
    ep = read_config_yaml(E2EApp.CONFIG_YAML)["profile_endpoint"]
    ep = "http://%s:%s/%s" % (ep["ip"], ep["port"], Profiles.CREATE_USER)
    click.echo("Creating user '%s'" % username)
    response = RestAPI.post_request(
        ep, {"username": username, "password": password,
             "firstname": first_name, "lastname": last_name})
    if response.status_code != 200:
        raise Exception("Requests status code: %s" % response.status_code)
    click.echo(response.json()["Msg"])


@profile.command()
@click.option('--flight_id', '-f', default=None, help='Flight Id')
@click.option('--num_seats', '-n', default=0, help='Required number of seats')
@click.option('--booking_class', '-c', default="economy",
              help='Booking class (economy / business)')
@click.option('--wallet', '-w', default=None,
              help='Wallet id to refer')
def book_flight(flight_id, num_seats, booking_class, wallet):
    if flight_id is None:
        flight_id = input("Flight id: ")
    while num_seats < 1:
        num_seats = int(input("Number of seats: "))
    if wallet is None:
        wallet = input("Wallet id: ")

    ep = read_config_yaml(E2EApp.CONFIG_YAML)["profile_endpoint"]
    ep = "http://%s:%s/%s" % (ep["ip"], ep["port"], Profiles.CONFIRM_BOOKING)
    click.echo("Booking flight '%s'" % flight_id)
    response = RestAPI.post_request(
        ep, {"username": E2EApp.USERNAME, "password": E2EApp.PASSWORD,
             "flightSeats": str(num_seats), "flightId": flight_id,
             "bankAccount": str(wallet), "bookingClass": booking_class})
    if response.status_code != 200:
        raise Exception("Requests status code: %s" % response.status_code)

    response = response.json()["Msg"]
    table_data = list()
    table_header = ["ID", "Flight Id", "Seats", "Booking class", "Net Amt",
                    "Wallet", "Status"]
    if response["status"] == "FAILED":
        table_header = [
            "ID", "Flight Id", "Seats", "Booking class", "Net Amt",
            "Wallet", "Status", "Failure Reason"]
        required_data = ["id", "flightId", "flightSeats", "bookingClass",
                         "ticket_cost", "bankAccount", "status",
                         "Booking failure reason"]
    else:
        required_data = ["id", "flightId", "flightSeats", "bookingClass",
                         "ticket_cost", "bankAccount", "status"]
    table_data.append([response[hdr] for hdr in required_data])
    click.echo(tabulate(table_data, headers=table_header,
                        tablefmt="fancy_grid"))


@profile.command()
def get_all_bookings():
    ep = read_config_yaml(E2EApp.CONFIG_YAML)["profile_endpoint"]
    ep = "http://%s:%s/%s" % (ep["ip"], ep["port"], Profiles.ALL_BOOKING)
    response = RestAPI.post_request(
        ep, {"username": E2EApp.USERNAME, "password": E2EApp.PASSWORD})

    if response.status_code != 200:
        raise Exception("Requests status code: %s" % response.status_code)

    booking_ids = response.json()["Msg"][0]["bookings"]
    table_data = list()
    table_header = ["Booking Id", "Flight Id", "Seats", "Class",
                    "Status", "Reason"]
    required_fields = ["id", "flightId", "flightSeats", "bookingClass",
                       "status"]
    click.echo("Fetching bookings for user '%s'" % E2EApp.USERNAME)
    for b_id in booking_ids:
        ep = read_config_yaml(E2EApp.CONFIG_YAML)["profile_endpoint"]
        endpoint = "http://%s:%s/%s" % (ep["ip"], ep["port"],
                                        Profiles.GET_BOOKING)
        response = RestAPI.post_request(endpoint,
                                        {"username": E2EApp.USERNAME,
                                         "password": E2EApp.PASSWORD,
                                         "id": b_id})
        if response.status_code != 200:
            raise Exception("Requests status code: %s" % response.status_code)

        response = response.json()["Msg"]
        table_row = [response[field] for field in required_fields]
        if "Booking failure reason" in response:
            table_row.append(response["Booking failure reason"])
        else:
            table_row.append("")
        table_data.append(table_row)

    click.echo(tabulate(table_data, headers=table_header,
                        tablefmt="fancy_grid"))


@profile.command()
@click.option('--booking_id', '-b', default=None, help='Booking id')
def get_booking(booking_id):
    if booking_id is None:
        booking_id = input("Booking id: ")
    ep = read_config_yaml(E2EApp.CONFIG_YAML)["profile_endpoint"]
    endpoint = "http://%s:%s/%s" % (ep["ip"], ep["port"],
                                    Profiles.GET_BOOKING)
    response = RestAPI.post_request(endpoint,
                                    {"username": E2EApp.USERNAME,
                                     "password": E2EApp.PASSWORD,
                                     "id": booking_id})
    if response.status_code != 200:
        raise Exception("Requests status code: %s" % response.status_code)

    response = response.json()["Msg"]
    click.echo(tabulate(
        [[response["flightId"], response["bookingClass"],
         response["flightSeats"], response["TicketsBooked"],
         response["ticket_cost"], response["status"]]],
        headers=["Flight Id", "Class", "Seat#", "Seat Details", "Net Amount",
                 "Status"],
        tablefmt="fancy_grid"))


@profile.command()
@click.option('--booking_id', '-b', default=None, help='Booking id')
def cancel_booking(booking_id):
    if booking_id is None:
        booking_id = input("Booking id: ")
    ep = read_config_yaml(E2EApp.CONFIG_YAML)["profile_endpoint"]
    ep = "http://%s:%s/%s" % (ep["ip"], ep["port"], Profiles.CANCEL_BOOKING)
    response = RestAPI.post_request(ep, {"username": E2EApp.USERNAME,
                                         "password": E2EApp.PASSWORD,
                                         "id": booking_id})
    if response.status_code != 200:
        raise Exception("Requests status code: %s" % response.status_code)

    response = response.json()['Msg']
    click.echo(tabulate(
        [[response["flightId"], response["bookingClass"],
          response["flightSeats"], response["ticket_cost"],
          response["status"]]],
        headers=["Flight Id", "Class", "Seat#", "Net Amount", "Status"],
        tablefmt="fancy_grid"))
