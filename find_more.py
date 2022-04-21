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
dbc.execute("select username from nonbots;")
nonbots = [i[0] for i in dbc]

print(nonbots)

dbc = db.cursor()
dbc.execute("select parent, id, hasbeenuserscraped from known_comments;")
parent = [i for i in dbc if not i[2]]

dbc = db.cursor()
dbc.execute("select username from bots;")
bots = [i[0] for i in dbc]

print("[initalization] Connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

def askuserifbot(uname):
    print(BOLD + "Link https://reddit.com/u/" + uname + RESET)
    a1 = input("Is this user a bot [y/n]") == 'y'
    a2 =input("Is this user a bot [y/n]") == 'y'
    if a1 is not a2:
        return askuserifbot(uname)
    else:
        return a1 & a2

for (pid,cid,hasbeenscraped) in parent:
    c = r.submission(pid[3:]);
    
    try:
        # Check for deleted author account
        if c.author != None:
            newbot = c.author.name
            if (not (newbot in bots)) and (not (newbot in nonbots)):
                print(BOLD + GREEN + "NEW BOT CANDIDATE '" + c.author.name + "'" + RESET)
                if askuserifbot(newbot):
                    dbc = db.cursor()
                    dbc.execute("insert into bots (username, notes) values (?, ?);", (newbot, "AUTOADD"))
                    bots.append(newbot)
                    db.commit()
                else:
                    dbc = db.cursor()
                    dbc.execute("insert into nonbots (username) values (?);", (newbot,))
                    db.commit()
                    nonbots.append(newbot)
        dbc = db.cursor()
        dbc.execute("update known_comments set hasbeenuserscraped=1 where id=?;", (cid,))

    except Exception as e:
        print(pid,cid);
        print(RED + " error " + str(e) + RESET)


db.commit() 
db.close()

print("[bot] done" + BELL)
