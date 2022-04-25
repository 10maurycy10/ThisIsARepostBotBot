import praw
import json
import mariadb

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
dbc.execute("select username from known_accounts")
user_list = [i[0] for i in dbc]

print("[initalization] Feching list of known comments")

dbc = db.cursor()
dbc.execute("select id from comments")
known_ids = [i[0] for i in dbc]

print("[initalization] Connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

is_id_known = {}

for post in known_ids:
    is_id_known[post] = True

for user in user_list[::-1]:
    user_handle = r.redditor(user);
    print("[bot] scraping " + user_handle.name)
    try:
        for comment in user_handle.comments.new(limit=20):
            if not str(comment) in is_id_known:
                print("[comment]" + GREEN + "grabing comment" + RESET)
                dbc = db.cursor()
                dbc.execute("insert into comments (id, text, username, parent) values (?, ?, ?, ?);", (str(comment.id), str(comment.body), comment.author.name, comment.parent_id))
                db.commit()
            else:
                print("[comment]" + RED +  " Skiping " + str(comment) + RESET)
    except Exception:
        pass

db.commit() 
db.close()

print("[bot] done" + BELL)
