# ThisIsARepostBotBot

> So you found a repost bot, now what?

This is a bot to reply to all posts of a repost bot with a message urging users to report and down vote, It can also report posts. (You may want a burner account for this.)

## Requirements

### reddit

A reddit account with a added script.

To add a script to your reddit account, go to https://old.reddit.com/prefs/apps, click "create (another) app", select "personal use script", and enter "http://localhost/" as the redirect uri.

(Keep the page open, you will need the client secret and client id values to configure the script)

### pip

- praw

- mariadb

### DB

This uses an MySQL/mariadb database to store lists of bot users and keep track of reported posts.

You can create the required table structure like this:

```sql
create database repost;
use repost;
create table bots (username: varchar(60));
create table reported_posts (id: varchar(10));
create index id on reported_posts (id);
```

## Configuration

The main configuration file is "config.json", a template file is provided, "config.json.exmple".

You will have to add the usernames of the repostbots into the ``bots`` table.

## Running

just ``python3 bot.py``
