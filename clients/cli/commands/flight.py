import urllib.parse

import click

from tabulate import tabulate

from constants.app import E2EApp
from constants.flights import Flights
from lib.common import common_options, read_config_yaml
from lib.rest_helper import RestAPI


@click.group()
def flight():
    pass


@flight.command()
@click.option('--airline', '-a', default=None, help='Airline name')
def get_flight(airline):
    if airline is None:
        airline = input("Airline name: ")

    click.echo("Get flights for '%s'" % airline)
    airline = urllib.parse.quote(airline)
    flights_data = list()
    flight_ep = read_config_yaml(E2EApp.CONFIG_YAML)["flight_endpoint"]
    endpoint = "http://%s:%s/%s/%s" \
               % (flight_ep["ip"], flight_ep["port"],
                  Flights.GET_FLIGHTS_FOR_AIRLINE, airline)

    response = RestAPI.get_request(endpoint)
    if response.status_code != 200:
        raise Exception("Requests status code: %s" % response.status_code)

    for f_data in response.json():
        f_data = f_data["flights"]
        flights_data.append(
            [f_data["flight_id"], f_data["model"],
             f_data["departing_airport"], f_data["arriving_airport"],
             f_data["departure_date"], f_data["status"]])

    click.echo(tabulate(flights_data,
                        headers=["Flight Id", "Model",
                                 "Departure", "Arrival",
                                 "Departure Time", "Status"],
                        tablefmt="fancy_grid"))
