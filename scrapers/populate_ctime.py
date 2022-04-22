# Populate null creation times in the db

import praw
import json
import mariadb

config = {}
with open("config.json", "r") as conffile:
    config = json.loads(conffile.read())

print("Connecting to DB")

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)

print("Feching bot list")

dbc = db.cursor()
dbc.execute("select (username) from bots where creationtime is null")
bot_list = [i[0] for i in dbc]

print("Connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

for bot in bot_list:
    user = r.redditor(bot)
    print(user.created_utc)
    dbc = db.cursor()
    dbc.execute("update bots set creationtime=? where username=?", (user.created_utc, bot))

db.commit() 
db.close()
