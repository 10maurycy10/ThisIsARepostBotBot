# use comment data to find bots
#
# create table nonbots (username VARCHAR(60) );
# create table bots (username VARCHAR(60), notes VARCHAR(256));
# create table known_comments (parent VARCHAR(10), id VARCHAR(10), hasbeenuserscrape BOOL)

import praw
import json
import mariadb

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

print("[initalization] Feching posts")

dbc = db.cursor()
dbc.execute("select username from known_accounts;")
knownaccounts = [i[0] for i in dbc]

print("[initalization] Connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

knownaccounts_dict = {}

for i in knownaccounts:
    knownaccounts_dict[i] = True

for user in knownaccounts[::-1]:
    c = r.redditor(user);
    try:
        for comment in c.comments.new(limit=20):
            if not comment.parent().author.name in knownaccounts_dict:
                new_account = comment.parent().author;
                knownaccounts.append(new_account.name)
                knownaccounts_dict[new_account.name] = True
                dbc = db.cursor()
                dbc.execute("insert into known_accounts (username, id, creationtime) values (?, ?, ?)", (new_account.name,new_account.id,new_account.created_utc));
                print(GREEN + "get new account! " + new_account.name + RESET);
                db.commit();
    except Exception as e:
        print(user);
        print(RED + " error " + str(e) + RESET)


db.commit() 
db.close()

print("[bot] done" + BELL)
