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
dbc.execute("select username from bots where dontflag is NULL or dontflag = 0")
bot_list = [i[0] for i in dbc]

print(bot_list)

print("[initalization] Feching subreddit black list")

dbc = db.cursor()
dbc.execute("select name from sub_blacklist")
sub_black_list = [i[0] for i in dbc]

print("[initalization] Feching list of reported posts")

dbc = db.cursor()
dbc.execute("select id from reported_posts")
flaged_posts = [i[0] for i in dbc]

print("[initalization] Connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

is_post_flaged = {}

for post in flaged_posts:
    is_post_flaged[post] = True

ignore_sub = {}

for sub in sub_black_list:
    ignore_sub[sub] = True

for bot in bot_list:
    reportedposts = 0
    bot_handle = r.redditor(bot);
    print("[bot] Reporting " + bot_handle.name)
    try:
        for post in bot_handle.submissions.new(limit = 5):
            if not(str(post) in is_post_flaged) and (not post.locked) and (not str(post.subreddit) in ignore_sub):
                print("[userflager] Flaging : " + str(post))
                reportedposts = reportedposts + 1
                try:
                    if config["repost_reply"] is not None:
                        post.reply(config["repost_reply"].format(bot));
                    if config["repost_report"]:
                        post.report("Spam")
                    dbc = db.cursor()
                    dbc.execute("insert into reported_posts (id) values (?)",  (str(post),))
                    db.commit()
                except Exception as e:
                    print(BOLD + RED+ "error flaging post, ratelimit or ban " + str(e) + RESET)
                if config["maxuserflags"] != None:
                    if config["maxuserflags"] <= reportedposts:
                        print("[userflaged] Bailing on " + str(bot));
                        break;
    
                print("[userflager]" + GREEN + " Flaged post " + post.shortlink + ", In sub " + str(post.subreddit) + RESET);
                is_post_flaged[str(post)] = True
            else:
                print("[userflager]" + RED +  " Skiping " + str(post) + " In sub " + str(post.subreddit) + RESET)
    except Exception as e:
        print(BOLD + RED + str(e) + RESET)

db.commit() 
db.close()

print("[bot] done" + BELL)
