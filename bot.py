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
dbc.execute("select username from bots")
bot_list = [i[0] for i in dbc]

print("Feching list of reported posts")

dbc = db.cursor()
dbc.execute("select id from reported_posts")
flaged_posts = [i[0] for i in dbc]

print("Connecting to reddit")

r = praw.Reddit(client_id=config['reddit_client_id'], client_secret=config['reddit_client_secret'], username=config["reddit_username"], password=config["reddit_passwd"], user_agent=config["reddit_ua"])

is_post_flaged = {}

for post in flaged_posts:
    is_post_flaged[post] = True

print(is_post_flaged)

for bot in bot_list:
    bot_handle = r.redditor(bot);
    print("Reporting " + bot_handle.name)
    for post in bot_handle.submissions.new():
        if not(str(post) in is_post_flaged):
            print("Flaging : " + str(post))
            if config["repost_reply"] is not None:
                post.reply(config["repost_reply"]);
            if config["repost_report"]:
                post.report("Spam")
            dbc = db.cursor()
            dbc.execute("insert into reported_posts (id) values (?)",  (str(post),))
            print("Shortlink : " + post.shortlink)
            is_post_flaged[str(post)] = True
        else:
            print("Skiping " + str(post));

db.commit() 
db.close()
