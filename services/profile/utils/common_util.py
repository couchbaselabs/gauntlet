import requests

from services.profile.utils.defaults import Default
from services.profile.utils.ldap_util import LdapUtil


class CommonUtil:
    def __init__(self, cb):
        self.cb = cb
        self.ldap_util = LdapUtil()

    @staticmethod
    def http_request(service, uri, method, body=None):
        if service == "booking":
            host = Default.booking_host
            port = Default.booking_port
        else:
            ex = "Unsupported service is requested"
            # TODO: When new services are supported from Profile endpoint
            print(str(ex))
            return False, str(ex), None

        url = f"http://{host}:{port}/{uri}"
        print("URL:Body - %s:%s" % (url, body))
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        try:
            response = requests.request(method, url, headers=headers,
                                        json=body)
        except (Exception, TypeError) as ex:
            print(str(ex))
            return False, str(ex), None

        if response.status_code in [200, 201, 202]:
            return True, response.json(), response.status_code
        else:
            return False, response.json(), response.status_code
