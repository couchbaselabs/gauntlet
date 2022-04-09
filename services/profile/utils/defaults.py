import os

class Default:
    # eagle-eye store information
    cb_username  = os.environ['CAPELLA_USERNAME']
    cb_password = os.environ['CAPELLA_PASSWORD']
    cb_host = os.environ['DB_HOSTNAME']
    booking_host = os.environ['BOOKING_HOST']
    booking_port = os.environ["BOOKING_PORT"]