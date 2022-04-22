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
dbc.execute("select username from bots")
bot_list = [i[0] for i in dbc]

print(bot_list)

print("[initalization] Feching list of known [psts")

dbc = db.cursor()
dbc.execute("select id from known_posts")
known_posts = [i[0] for i in dbc]

print("[initalization] Connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

is_post_known = {}

for post in known_posts:
    is_post_known[post] = True

for bot in bot_list:
    bot_handle = r.redditor(bot);
    print("[bot] Reporting " + bot_handle.name)
    for post in bot_handle.submissions.new():
        if not str(post) in is_post_known:
            print("[postscraper]" + GREEN + "grabing post" + RESET)
            dbc = db.cursor()
            dbc.execute("insert into known_posts (title, subreddit, username, id) values (?, ?, ?, ?);", (post.title, str(post.subreddit), post.author.name, post.id))
        else:
            print("[postscraper]" + RED +  " Skiping " + str(post) + " In sub " + str(post.subreddit) + RESET)

db.commit() 
db.close()

print("[bot] done" + BELL)
