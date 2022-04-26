#!/bin/sh
cd /home/mz/prog/repostbot

if [[ -z $(pidof chisel) ]]
then
	#echo python get_comments.py
	#timeout 10m python scrapers/get_bot_comments.py

	#echo python get_posts.py
	#timeout 10m python scrapers/get_bot_posts.py
	
	timeout 10m python scrapers/prune_bot_list.py

	echo python bot.py
	timeout 10m python bot/bot.py
else
	#echo pproxychains ython get_comments.py
	#timeout 10m proxychains python scrapers/get_bot_comments.py

	#echo proxychains python get_posts.py 
	#timeout 10m proxychains python scrapers/get_bot_posts.py
	timeout 10m proxychains python scrapers/prune_bot_list.py

	echo proxychains python bot.py
	timeout 10m proxychains python bot/bot.py
fi
