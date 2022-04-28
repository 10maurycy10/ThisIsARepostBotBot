# One Script to rule them all, 
# One script to find them; 
# One script to bring them all
# and in the darkness bind them.

import mariadb
import json
import tensorflow as tf
import praw
import prawcore

# colors for prity logs
RED = '\x1b[31m'
BLUE = '\x1b[94m'
GREEN = '\x1b[32m'
RESET = '\x1b[0m'
BOLD = '\x1b[1m'
BELL = '\a'

print("[initalization] Loading config file")

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

m = tf.keras.models.load_model("corelation/tfisbot")

print("[initalization] connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

print("[initalization] fetching account list")

# Find known accounts that are not flaged as bot or non bots
db.commit()
dbc = db.cursor()
dbc.execute("select username from known_accounts where not username in (select username from bots) and not username in (select username from nonbots);")
users = [i[0] for i in dbc]
db.commit()


# Find known accounts that are not flaged as bot or non bots
dbc = db.cursor()
dbc.execute("select username from known_accounts;")
known_accounts = [i[0] for i in dbc]
db.commit()

print("[initalization] fetching comment list")
dbc = db.cursor()
dbc.execute("select id from comments;")
known_ids = [i[0] for i in dbc]
db.commit()


# check is a user exis and is not banned
def is_stale(username):
    try:
        u = r.redditor(username)
        #r.username
        for i in u.submissions.new(limit=1):
            pass
        for i in u.comments.new(limit=1):
            pass
        return False
    except prawcore.exceptions.NotFound:
        return True

# get comments for a user, and add them into the DB
def get_user_comments(username):
    print("[get_user_comments] " + GREEN + "getting comments for " + username + RESET)
    user_handle = r.redditor(username);
    for comment in user_handle.comments.new(limit=20):
        if not str(comment) in known_ids:
            dbc = db.cursor()
            dbc.execute("insert into comments (id, text, username, parent, subreddit) values (?, ?, ?, ?, ?);", (str(comment.id), str(comment.body), comment.author.name, comment.parent_id, str(comment.subreddit)))
            db.commit()

# requires get_user_comments to be called
def check_user(username):
    dbc = db.cursor()
    dbc.execute("select text from comments where username=? limit 20;", (username,))
    comments = [text[0] for text in dbc]
    db.commit()
    if len(comments) == 0:
        print(BOLD + RED + "[nlp] check_and_add_user called on username '" + username + "' with no known comments!! fix you code" + RESET)
        return
    scores = m.predict(comments)
    bias = -min(20, len(scores)) / 10 # A bais to avoid flaging users with low comment count
    score =  sum(scores) / len(scores) + bias
    print("[nlp] user '" + username + "' has score " + str(score))
    return score

def get_accounts(username):
    user = r.redditor(username)
    for post in user.submissions.new(limit=20):
        count = 0
        new_count = 0
        for comment in post.comments:
            if count > 10:
                return;
            count = count + 1
            if not comment.author in known_accounts:
                known_accounts.append(username)
                print(GREEN+ "[get_accounts] found new user: " + str(comment.author) + RESET)
                dbc = db.cursor()
                dbc.execute("insert into known_accounts (username) values (?);", (str(comment.author),))
                db.commit()
                new_count = new_count + 1
                if new_count > 5:
                    return

# check is a user is a bot and scrape more accounts
def do_user(username):
    get_user_comments(username)
    if check_user(username) > 0.4:
        print(GREEN +  "[user] found bot '" + username + "'")
        bot = r.redditor(username)
        dbc = db.cursor()
        dbc.execute("insert into bots (username, creationtime, notes, mladd) values (?, ?, ?, 1);", (username, bot.created_utc, "One script to find them all and in the darkness bind them"))
        db.commit()
    get_accounts(username)

dbc = db.cursor()
dbc.execute("select username from known_accounts where foundthemall is null");
users_to_check = [i[0] for i in dbc]
db.commit()

for username in users_to_check:
    if not is_stale(username):
        do_user(username)
        dbc = db.cursor()
        dbc.execute("update known_accounts set foundthemall=1 where username=?;", (username,))
        db.commit()
        
    
