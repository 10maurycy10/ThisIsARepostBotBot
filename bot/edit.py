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

print("[initalization] Connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

for comment in r.redditor(config['reddit_username']).comments.new(limit=1000):
    if "100 days old" in comment.body:
        print("changing " + str(comment))
        try:
            comment.edit(config["repost_reply"].format(comment.parent().author.name))
        except:
            print(RED + BOLD + "error + " + comment.permalink + RESET)

print("[bot] done" + BELL)
