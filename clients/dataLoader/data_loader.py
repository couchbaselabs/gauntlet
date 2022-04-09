import os, json
from clients.dataLoader.utils.defaults import Default
from clients.dataLoader.utils.cb_util import CBConnection

script_dir = os.path.dirname(os.path.realpath(__file__))


class DataLoader:
    def __init__(self):
        self.cb = CBConnection(Default.cb_username, Default.cb_password, Default.cb_host, Default.cb_bucketname)

    def loadData(self):
        with open(script_dir + '/schema.json', 'r') as schemaFile:
            dataSchema = json.load(schemaFile)
            for scopeName in dataSchema:
                self.cb.createScope(scopeName)
                scopeSchema = dataSchema[scopeName]
                for collectionName in scopeSchema:
                    self.cb.createCollection(collectionName,scopeName)
                    collectionSchema = scopeSchema[collectionName]
                    for documentName in collectionSchema:
                        self.cb.upsertDocument(scopeName,collectionName,documentName)

if __name__ == "__main__":
    DataLoader().loadData()



