import os, json
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.management.collections import CollectionSpec
from couchbase.management.buckets import BucketType,CreateBucketSettings,ConflictResolutionType

from couchbase_core.cluster import PasswordAuthenticator
from couchbase.exceptions import ScopeAlreadyExistsException, CollectionAlreadyExistsException, \
    BucketAlreadyExistsException

script_dir = os.path.dirname(os.path.realpath(__file__))


class CBConnection:
    def __init__(self, username, password, host, bucketName):
        self.cluster = Cluster("couchbase://{0}?ssl=no_verify".format(host), ClusterOptions(
            PasswordAuthenticator(username, password)
        ))
        self.bucketName = bucketName
        self.bucket = None
        self.coll_manager = None
        self.createBucket(self.bucketName)

    def createBucket(self, bucketName):
        bucket_manager = self.cluster.buckets()
        try:
            print("Creating bucket: {}".format(bucketName))
            bucket_manager.create_bucket(
                CreateBucketSettings(
                    name= bucketName,
                    flush_enabled=True,
                    ram_quota_mb=100,
                    num_replicas=0,
                    conflict_resolution_type=ConflictResolutionType.SEQUENCE_NUMBER,
                    bucket_type=BucketType.COUCHBASE))
        except BucketAlreadyExistsException:
            print("Bucket: {} already exists. So not creating it again".format(bucketName))

        self.bucket = self.cluster.bucket(bucketName)
        self.coll_manager = self.bucket.collections()
        return

    def createScope(self, scopeName):
        try:
            print("creating scope: {}".format(scopeName))
            self.coll_manager.create_scope(scopeName)
        except ScopeAlreadyExistsException:
            print("scope: {} already exists. So not creating it again".format(scopeName))


    def createCollection(self, collectionName,scopeName):
        try:
            print("creating Collection: {} under scope {}".format(collectionName,scopeName))
            collection_spec = CollectionSpec(collectionName,scope_name=scopeName)
            self.coll_manager.create_collection(collection_spec)
        except CollectionAlreadyExistsException:
            print("Collection: {} already exists. So not creating it again".format(collectionName))


    def upsertDocument(self,scopeName, collectionName, documentName):
        print("creating document {} in collection {} under scope {}".format(documentName,collectionName,scopeName))
        collection = self.bucket.scope(scopeName).collection(collectionName)
        with open(script_dir + '/../json/'+documentName, 'r') as schemaFile:
            docContent = json.load(schemaFile)
            docId = docContent["docId"]
            collection.upsert(docId,docContent)



