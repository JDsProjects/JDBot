import os, pymongo, dns, motor, motor.motor_asyncio

DB_logindetails = str(os.environ['DB_data'])
DB_client = motor.motor_asyncio.AsyncIOMotorClient(DB_logindetails)

db = DB_client.JDBot_data
content_database=db.list_collection_names()
db.money_system.create_index([('user_id', pymongo.ASCENDING)],unique=True)
db.guild_prefixes.create_index([('ser_id', pymongo.ASCENDING)],unique=True)
db.job_listing.create_index([('job_id', pymongo.ASCENDING)],unique=True)
db.spy_co_data.create_index([('game_id', pymongo.ASCENDING)],unique=True)