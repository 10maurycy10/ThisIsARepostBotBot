from joblib import dump, load
import praw
import json
import mariadb
import asyncio
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import losses
import numpy as np


RED = '\x1b[31m'
BLUE = '\x1b[94m'
GREEN = '\x1b[32m'
RESET = '\x1b[0m'
BOLD = '\x1b[1m'
BELL = '\a'

# Load configug file
config = {}
with open("config.json", "r") as conffile:
    config = json.loads(conffile.read())

print("[initalization] Connecting to DB")

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)

print("[initalization] Loading models")

m = tf.keras.models.load_model("tfisbot")

print("[initalization] geting list of users")

dbc = db.cursor()
dbc.execute("select * from known_accounts where not username in (select username from bots);")
users = [i for i in dbc]

print("[initalization] connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

print("[initalization] done")

def askuserifbot(uname):
    print(BOLD + "Link https://reddit.com/u/" + uname + RESET)
    a1 = input("Is this user a bot [y/n]") == 'y'
    a2 =input("Is this user a bot [y/n]") == 'y'
    if a1 is not a2:
        return askuserifbot(uname)
    else:
        return a1 & a2

print(m.predict(["test data"]))



def douser(name):
        user_handle = r.redditor(name)
        print("[scraper] getting comments")
        dbc = db.cursor()
        dbc.execute("select text from comments where username=? limit 10;",(name,))
        comments = [comment[0] for comment in dbc]
        print("[math] vectorizing comments + ")
        comments_scored = m.predict(comments)
        print("[math] calculationg score")
        count = 0
        total_score = 0
        for score in comments_scored:
            count = count + 1
            total_score = total_score + score
        if count > 0:
            score = total_score / count
            print(name + " has score " + str(score))
            if score > .5:
                print(BOLD + GREEN + "FOUND LIKLEY BOT!! https://www.reddit.com/u/" + name + RESET)
                if askuserifbot(name):
                    dbc = db.cursor()
                    dbc.execute("insert into bots (username, notes) values (?, ?); ", (name, "Classifyer go brrr"))
                    db.commit()
                else:
                    dbc = db.cursor()
                    dbc.execute("insert into nonbots (username) values (?,); ", (name,))
                    db.commit()

douser("Epikest")

for user in users[::-1]:
    try:
        douser(user[0])
    except Exception as e:
        print(RED + "Error " + str(e) + RESET);
