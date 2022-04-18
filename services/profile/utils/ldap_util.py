import ldap


class LdapUtil(object):
    def __init__(self):
        self.base_dn = "ou=e2e_app,dc=couchbase,dc=com"
        self.ldap_server = "ldap://172.23.120.205:389"
        self.admin_user = "cn=Manager,dc=couchbase,dc=com"
        self.admin_password = "p@ssword"

        self.connection = None

    def __connect(self):
        self.connection = ldap.initialize(self.ldap_server)
        self.connection.protocol_version = ldap.VERSION3

    def __disconnect(self):
        self.connection.unbind_s()

    def authenticate(self, username, password):
        username = "uid=%s,%s" % (username, self.base_dn)
        try:
            self.__connect()
            self.connection.simple_bind_s(username, password)
            self.__disconnect()
            return True
        except Exception as error:
            print("Ldap exception: %s" % error)
        return False

    def create_user(self, params):
        username = params["username"]
        first_name = params["firstname"]
        last_name = params["lastname"]
        password = params["password"]
        full_name = "%s %s" % (first_name, last_name)
        dn = 'uid=%s,%s' % (username, self.base_dn)

        entry = list()
        entry.extend([
            ('objectClass', ['inetOrgPerson'.encode('utf-8')]),
            ('uid', [username.encode('utf-8')]),
            ('cn', [full_name.encode('utf-8')]),
            ('sn', [last_name.encode('utf-8')]),
            ('userPassword', [password.encode('utf-8')])
        ])

        try:
            self.__connect()
            self.connection.simple_bind_s(self.admin_user, self.admin_password)
            self.connection.add_s(dn, entry)
            self.__disconnect()
        except Exception as e:
            print("Ldap user create failed: %s" % e)
            return False
        return True

    def delete_user(self, params):
        username = params["username"]
        dn = 'uid=%s,%s' % (username, self.base_dn)

        try:
            self.__connect()
            self.connection.simple_bind_s(self.admin_user, self.admin_password)
            self.connection.delete_s(dn)
            self.__disconnect()
        except Exception as e:
            print("Ldap user delete failed: %s" % e)
            return False
        return True
