import json
import random
from joblib import dump, load
import mariadb
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer

def clean(data):
    return re.sub("[^a-z ]", "", re.sub("[,,/'\\(\\)]", " ", data.lower()))


#def standardize(input_data):
    #lowercase = tf.strings.lower(input_data)
    #nospecal = tf.strings.regex_replace(lowercase, '[^a-z ]', ' ')
    #return nospecal

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

print("feching dataset")
dbc = db.cursor()
dbc.execute("select text from known_comments;");
botcomments = [(clean(i[0]), 1) for i in dbc];

dbc = db.cursor()
dbc.execute("select text from comments where not id in (select username from known_comments);");
nonbotcomments = [(clean(i[0]), 0) for i in dbc];

print("preoccesing dataset")

comments = nonbotcomments + botcomments

random.shuffle(comments)

data = comments[1000:]
test_data = comments[:1000]

with open("test.json","w") as f:
    f.write(json.dumps(test_data))

#word_to_idx = {}
#for sent, _ in comments:
    #for word in sent:
        #if word not in word_to_idx:
            #word_to_idx[word] = len(word_to_idx)

#with open("word_to_idx.json", "w") as out:
    #out.write(json.dumps(word_to_idx))


train_text = [t[0] for t in data];
train_target = [t[1] for t in data];
test_text = [t[0] for t in test_data];
test_target = [t[1] for t in test_data];



#train_text = [[word_to_idx[word] for word in line] for line in train_text]


#vectorizer = vectorizer.build_analyzer()

print("creating vectorizer")

vectorizer = CountVectorizer()
vectorizer.fit_transform(train_text)
dump(vectorizer, 'vect.joblib')

print("vectorizing dataset")

train_text = vectorizer.transform(train_text)
test_text = vectorizer.transform(test_text)

print("training classifyer")

#from sklearn.naive_bayes import MultinomialNB
#clf = MultinomialNB()

from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(n_estimators=10)

#from sklearn.neural_network import MLPClassifier
#clf = MLPClassifier(solver='adam', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)

clf.fit(train_text, train_target)
print("classifyer has acuracy" + str(clf.score(test_text, test_target)))

dump(clf, 'isbot.joblib')


NUM_LABELS = 2

