from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator
from couchbase.exceptions import DocumentExistsException, \
    DocumentNotFoundException
from services.profile.utils.constants import Queries


class CBConnection:
    def __init__(self, username, password, host):
        self.cluster = Cluster("couchbase://{0}?ssl=no_verify".format(host),
                               ClusterOptions(PasswordAuthenticator(
                                   username, password)))

        self.cb = self.cluster.bucket("e2e")
        self.cb_coll = self.cb.scope("profiles").collection("users")

    def add_user(self, firstname, lastname, username, password, pass_id):
        # logger.info("Inserting Document")
        doc = {"firstname": firstname, "lastname": lastname,
               "username": username, "password": password,
               "bookings": [], "id": pass_id}
        try:
            self.cb_coll.insert(f'{firstname}_{lastname}', doc)
            return True
        except DocumentExistsException:
            return False

    def delete_user(self, firstname, lastname):
        try:
            self.cb_coll.remove(f'{firstname}_{lastname}')
        except DocumentNotFoundException:
            pass
        return True

    def get_user(self, user):
        query = Queries.get_user_password.format(user)
        return self.run_query(query)

    def get_user_id(self, user):
        query = Queries.get_user_id.format(user)
        return self.run_query(query)

    def get_all_bookings(self, user):
        query = Queries.get_all_bookings.format(user)
        return self.run_query(query)

    def run_query(self, query):
        res = self.cb.query(query)
        result_arr = [x for x in res]
        print(result_arr)
        return result_arr

    def update_user(self, username, booking_id):
        query = Queries.update_bookings.format(booking_id, username)
        _ = self.run_query(query)

    def get_api_details(self, service, uri):
        api_details = None
        query = Queries.get_api_details.format(service, uri)
        print(query)
        res = self.cb.query(query)
        print(res)
        result_arr = [x for x in res]
        if len(result_arr) != 0:
            api_details = result_arr[0]
        return api_details
