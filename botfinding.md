# How to find bots

## Manual method

This works on repost bots as well as spambots, Hovever it reqires manual checking for each account.

You will need some inital entrys in the ``bots`` table.

0. run scrapers/get_bot_comments.py

1. run corelation/find_more.py

## Automatic bot detection

This olny works on bots with a large list of ``bots`` and ``known_accounts``, the bots table can be populated useing the manual method, while the ``known_accounts`` table can be filled with the ``scrapers/find_accounts.py`` script.

It also requires a comment database, which you can populate with ``scrapers/get_bot_comments.py`` and ``scrapers/get_comments.py``

### Training

First you should make sure that as many bot are in the ``bots`` table. Then run ``corelation/nlp_tf.py`` to construct a classifyer.

### Testing

You cant run ``corelation/find_more_tf_nlp.py`` witch will go through the known_accounts db showing the bot scores for users, as well as having the option to mark them as bots or nonbots.

### Running

You can run the ``corelation/find_more_nlp_tf_fullauto.py`` to add users with a high bot score to the bot list.

You will also need to run ``scrapers/get_comments.py`` and ``scrapers/find_accounts.py``.
