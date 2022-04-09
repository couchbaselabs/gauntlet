from flask import Flask
from flask_restful import Api
import logging
from services.profile.endpoints.booking import ConfirmBooking, AllBookings, CreateUser, CancelBooking, GetBooking, EditBooking, UserAuth
from services.profile.utils.cb_util import CBConnection
from services.profile.utils.common_util import CommonUtil
from services.profile.utils.defaults import Default


class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)

        logging.basicConfig(filename="./server.log", level=logging.INFO,
                            format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

        self.cb = CBConnection(Default.cb_username, Default.cb_password, Default.cb_host)
        self.common_util = CommonUtil(self.cb)

        self.api.add_resource(UserAuth, '/user_auth', resource_class_args=(self.cb,self.common_util))
        self.api.add_resource(ConfirmBooking, '/confirmBooking', resource_class_args=(self.cb,self.common_util))
        self.api.add_resource(AllBookings, '/allBookings', resource_class_args=(self.cb,self.common_util))
        self.api.add_resource(GetBooking, '/getBooking', resource_class_args=(self.cb,self.common_util))
        self.api.add_resource(CreateUser, '/createUser', resource_class_args=(self.cb,self.common_util))
        self.api.add_resource(CancelBooking, '/cancelBooking', resource_class_args=(self.cb,self.common_util))
        self.api.add_resource(EditBooking, '/editBooking', resource_class_args=(self.cb,self.common_util))

    def run(self):
        self.app.run(host='0.0.0.0', debug=True)


if __name__ == '__main__':
    App().run()
