import pymongo
import urllib.parse
username = urllib.parse.quote_plus('admin')
password = urllib.parse.quote_plus('asdasd@123')
client = pymongo.MongoClient("mongodb+srv://" + username + ":" + password+ "@cluster0.le7xd.mongodb.net/?retryWrites=true&w=majority")
db = client['apadgroup8']
print(db.list_collection_names())
