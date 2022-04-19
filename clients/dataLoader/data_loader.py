import json
import os
from clients.dataLoader.utils.defaults import Default
from clients.dataLoader.utils.cb_util import CBConnection

script_dir = os.path.dirname(os.path.realpath(__file__))


class DataLoader:
    def __init__(self):
        self.cb = CBConnection(Default.cb_username, Default.cb_password,
                               Default.cb_host, Default.cb_bucketname)

    def load_data(self):
        with open(script_dir + '/schema.json', 'r') as schemaFile:
            data_schema = json.load(schemaFile)
            for scopeName in data_schema:
                self.cb.createScope(scopeName)
                scope_schema = data_schema[scopeName]
                for collectionName in scope_schema:
                    self.cb.createCollection(collectionName, scopeName)
                    collection_schema = scope_schema[collectionName]
                    for documentName in collection_schema:
                        self.cb.upsertDocument(scopeName, collectionName,
                                               documentName)


if __name__ == "__main__":
    DataLoader().load_data()
