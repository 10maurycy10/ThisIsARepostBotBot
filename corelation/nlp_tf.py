import json
import random
from joblib import dump, load
import mariadb
import pandas as pd
import re
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import losses

def clean(data):
    print(data)
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
botcomments = [(i[0], 1) for i in dbc];

dbc = db.cursor()
dbc.execute("select text from comments where not id in (select username from known_comments) and mladd!=1;");
nonbotcomments = [(i[0], 0) for i in dbc];

print("preoccesing dataset")

comments = nonbotcomments + botcomments

random.shuffle(comments)

data = comments[1000:10000]
test_data = comments[:1000]

with open("test.json","w") as f:
    f.write(json.dumps(test_data))

train_text = [t[0] for t in data];
train_target = [t[1] for t in data];
test_text = [t[0] for t in test_data];
test_target = [t[1] for t in test_data];

#train_ds = tf.data.Dataset.from_tensor_slices((train_text, train_target))
#test_ds = tf.data.Dataset.from_tensor_slices((test_text, test_target))

print("creating vectorizer")

max_features = 10000
sequence_length = 250

vectorize_layer = layers.TextVectorization(
    standardize='lower_and_strip_punctuation',
    max_tokens=max_features,
    output_mode='int',
    output_sequence_length=sequence_length
)

vectorize_layer.adapt(train_text)

print("vectorizing dataset")

#train_text = vectorize_layer.transform(train_text)
#test_text = vectorize_layer.transform(test_text)

print("training classifyer")

model = tf.keras.Sequential([
    vectorize_layer,
    tf.keras.layers.Embedding(
        input_dim=len(vectorize_layer.get_vocabulary()),
        output_dim=64,
        # Use masking to handle the variable sequence lengths
        mask_zero=True),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1)
])
    
model.summary()

model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    optimizer=tf.keras.optimizers.Adam(1e-4),
    metrics=['accuracy'])

model.fit(x=train_text, y=train_target, epochs=1,
                    validation_data=(test_text, test_target),
                    validation_steps=30)

print(model.predict(["This is not a bot like sentence"]))

model.save("tfisbot2")

