import praw
import json
import mariadb
import prawcore

# color escape codes

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
print("[initalization] Feching bot list")

dbc = db.cursor()
dbc.execute("select username from bots")
bot_list = [i[0] for i in dbc]

print("[initalization] Connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

for bot in bot_list:
    print("[bot] checking " + bot)
    try:
        bh = r.redditor(bot);
        for sub in bh.submissions.new(limit=1):
            pass
        print("fine")
    except prawcore.exceptions.NotFound:
        print(GREEN + "Found stale entry! " + bot + RESET);
        dbc = db.cursor()
        dbc.execute("delete from bots where username=?", (bot,));
        db.commit()
    except prawcore.exceptions.Forbidden:
        print(GREEN + "Found stale entry! " + bot + RESET);
        dbc = db.cursor()
        dbc.execute("delete from bots where username=?", (bot,));
        db.commit()


db.commit() 
db.close()

print("[bot] done" + BELL)
