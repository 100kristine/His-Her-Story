import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

from contextlib import closing
import pickle,nltk,gensim,string
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from collections import defaultdict
import numpy as np
from operator import itemgetter
from gensim import models
from gensim import corpora,similarities
from gensim.corpora import TextCorpus, MmCorpus,Dictionary

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

#NLP backend logic
stemmer = PorterStemmer()
currUrls = []
data = pickle.load(open('tagged_tokenized_data_full_fromTheBride','r'))

def stem(tokens,stemmer):
    # Stem tokens
    return [stemmer.stem(item) for item in tokens]

def tokenize(text):
    tokens = [i.lower() for i in nltk.word_tokenize(text) if i not in string.punctuation]
    return stem(tokens,stemmer)

def getSimilarities(tokens,id2word,index,lsi):
    #make sure tokens are stemmed
    #higher is more similar <-1,1>
    """>>> getSimilarities(tokens,index,lsi)
    [(0, 0.19454564),
     (1, 0.20364338),
     (2, 0.32875058),
     (3, 0.28404596)]
    """
    return list(enumerate(index[lsi[id2word.doc2bow(tokens)]]))

def getTopN(met,wishes,n=3):
    tokens = tokenize(met) + [" "] + tokenize(met)
    keys = pickle.load(open('keys','r'))
    lsi = pickle.load(open('lsi_model','r'))
    index = pickle.load(open('index.pickle','r'))
    id2word = pickle.load(open('id2word.pickle','r'))
    similarities = getSimilarities(tokens,id2word,index,lsi)
    top = sorted(similarities,key=itemgetter(1))[-n:]
    return [keys[item[0]] for item in top]

#end NLP backend logic

#def load_results():
            
#    return render_template('results.html',entries=[])    

def validate():
    return True

class myForm(Form):
    name = StringField('name', validators=[DataRequired()])



@app.route('/',methods=['POST','GET'])
def home():
    global stemmer,currUrls,start,data
    #if request.method == 'POST':
    #    print 'POST',request
    #form = myForm()
    #if form.validate_on_submit():
    #    print "validated"
    #    Met = request.args.get('Met', '')
    #    Type = request.args.get('Type', '')
    #    currUrls = getTopN(Met,Type,n=3)
    #    print "success"
    #    return redirect('/success')

    if request.method == 'GET':
        
        Met = request.args.get('Met', '')
        Type = request.args.get('Type', '')

        if len(Met) > 0:
            top = getTopN(Met,Type,n=3)
            print "MET",Met
            #for i in top:
            #    g.db.execute('insert into entries (title) values (?)',(i,))
            #    g.db.commit()
            names = [ ' '.join(t.split('/')[-2].split('-')) for t in top]
            descriptions = [data[t]['paragraphs'][0] for t in top]

            lst = []
            for i in range(len(top)):
                lst.append({'url':top[i],'name':names[i],'description':descriptions[i]+"..."})
            return render_template('results.html',entries=lst)    

    return render_template('home.html',name="home")

@app.route('/success')
def success():
    return render_template('results.html',entries=currUrls)

def getEntries():
    cur = g.db.execute('select title from entries order by id desc')
    return [dict(title=row[0]) for row in cur.fetchall()]

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
        
if __name__ == '__main__':
    app.run(debug=True)





