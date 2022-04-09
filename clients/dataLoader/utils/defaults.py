import os

class Default:

    cb_host = os.environ['DB_HOSTNAME']
    cb_username  = os.environ['CAPELLA_USERNAME']
    cb_password = os.environ['CAPELLA_PASSWORD']
    cb_bucketname = "e2e_poc"