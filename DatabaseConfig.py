import os
import pymongo
#it broke before without it so.
DB_logindetails = str(os.environ['DB_data'])
DB_client = pymongo.MongoClient(DB_logindetails)

db = DB_client.db_name
content_database=db.list_collection_names()
db.users_testing.create_index([('user_id', pymongo.ASCENDING)],unique=True)
db.g_link_testing.create_index([('ser_id', pymongo.ASCENDING)],unique=True)
db.server_settings.create_index([('ser_id',pymongo.ASCENDING)],unique=True)
db.update_note.create_index([('ser_id',pymongo.ASCENDING)],unique=True)
db.color_code.create_index([('user_id',pymongo.ASCENDING)],unique=True)