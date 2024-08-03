# ThisIsARepostBotBot

This is a loose collection of scripts intended to semi-automaticly built a list of bot accounts by either trying to detect bot like comments, or by tracking inter-bot interactions.

### DB

This uses an MySQL/mariadb database to store lists of bot users and keep track of reported posts.

You can create the required table structure like this:

```sql
create database repost;
use repost;
create table bots (username: varchar(60). creationtime INT, notes: varchar(256), dontflag BOOL, mladd BOOL); -- Add known bot accounts in here
create table reported_posts (id: varchar(10)); -- ids of posts that the bot has reported
create index id on reported_posts (id);
create table sub_blacklist (name: varchar(20)); -- Add subreddits without the 'r/' that you do *not* want to post on.
create table known_comments (id VARCHAR(10), text TEXT, parent VARCHAR(10), username VARCHAR(64), subreddit VARCHAR(64), hasbeenuserscraped BOOL); -- comments made by bots
create table comments (id VARCHAR(10), text TEXT, parent VARCHAR(10), username VARCHAR(64), subreddit);
create table nonbots (username VARCHAR(64));
create table known_accounts (username VARCHAR(64), id VARCHAR(10), creationtime INT, foundthemall BOOL, suspected_bot BOOL)
```

## Configuration

The main configuration file is "config.json", a template file is provided, "config.json.exmple".

You will have to add the usernames of the repostbots into the ``bots`` table.

# Scripts in repo

## python3 bot/bot.py

Comment on bot posts warning about the bot.

## scrapers/find_accounts.py

Add more users to the known_accounts table

## scrapers/get_comments.py

Gets comments from normal users

## scrapers/get_bot_comments.py

Pulls the comments of all bots from reddit.

## scrapers/get_bot_posts.py

Pulls the posts of all bots from reddit.

## corelation/find_more.py

Attempts to use the comment db to find other bot users running on the same instance, Promping the user to check if they are bots.

This requires ``get_comments.py`` to be run

## corelation/nlp_tf.py

Uses the database of comments and bot comments to construct a classifer

## one_script_to_find_them_all_and_in_the_darkness_bind_them.py

Requires the classifyer from ``nlp_tf.py``, Finds bot fully automaticly

