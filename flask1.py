from flask import Flask, render_template, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from db_setup import init_db, db_session
from forms import GameSearchForm
import numpy as np
import re
import operator

#pip install flask
#pip install flask-wtf
#pip install flask-sqlalchemy
#pip install flask_table

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/discorn/mysite/games.db'
app.secret_key = "115lol"
db = SQLAlchemy(app)

class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    QueryName = db.Column(db.String(75), nullable=False)
    ReleaseDate = db.Column(db.String(20), nullable=True)
    Metacritic = db.Column(db.Integer, nullable=True)
    RecommendationCount = db.Column(db.Integer, nullable=True)
    PriceInitial = db.Column(db.String(10), nullable=False)
    AboutText = db.Column(db.String(350), nullable=False)
    tfidfScore = 0.0

    def __init__(self, id, QueryName, ReleaseDate, Metacritic, RecommendationCount, PriceInitial, AboutText):
        self.id = id
        self.QueryName = QueryName
        self.ReleaseDate = ReleaseDate
        self.Metacritic = Metacritic
        self.RecommendationCount = RecommendationCount
        self.PriceInitial = PriceInitial
        self.AboutText = AboutText
        self.tfidfScore = 0.0

    #def __repr__(self):
        #return [self.QueryName, self.ReleaseDate]
        #return '<Games %r>' % self.QueryName
    #def __repr__(self):
     #   return "Game('{self.QueryName}', '{self.ReleaseDate}','{self.Metacritic}','{self.RecommendationCount}','{self.PriceInitial}','{self.AboutText}')"

@app.route('/', methods=['GET', 'POST'])
def index():
    search = GameSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', form=search)

@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
    search_string_vector = np.unique(re.split('[-_;:?<>() |, |/*|\n.!-+\t]', search_string.lower())).tolist()
    while search_string_vector.count(''):
        search_string_vector.remove('')


    if search_string:
        """if search.data['select'] == 'AboutText':
            qry = db_session.query(Games).filter(Games.AboutText.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'QueryName':
            qry = db_session.query(Games).filter(Games.QueryName.contains(search_string))
            results = qry.all()
        else:
            qry = db_session.query(Games)
            results = qry.all()"""
        #qry = db_session.query(Games).filter(Games.AboutText.contains(search_string))
        #results = qry.all()
        qry = db_session.query(Games)
        results = qry.all()

        numofDoc = len(results)
        numofWordSearch = len(search_string_vector)

        #IDF
        IDF = np.zeros(numofWordSearch).tolist()
        for i in range(numofWordSearch):
            qry2 = db_session.query(Games).filter(Games.AboutText.contains(search_string_vector[i]))
            results2 = qry2.all()
            IDF[i] = np.log(numofDoc/(1+len(results2)))

        #TF
        doc = np.zeros((numofDoc, numofWordSearch)).tolist()
        for i in range(0, numofDoc):
            postsplit = re.split('[-_;:?<>() |, |/*|\n.!-+\t]', results[i].AboutText.lower())
            while postsplit.count(''):
                postsplit.remove('')
            numofWordDoc = len(postsplit)
            tfidfScore_sum = 0.0
            for j in range(0, numofWordSearch):
                doc[i][j] = postsplit.count(search_string_vector[j]) / (1+numofWordDoc)
                #TF-IDF
                tfidfScore_sum = tfidfScore_sum + (doc[i][j] * IDF[j])
            results[i].tfidfScore = tfidfScore_sum

    else:
        qry = db_session.query(Games)
        results = qry.all()

    if not results:
        flash('No results found.')
        return redirect('/')
    else:
        """
        results[0].QueryName = 'asdasd'
        qry = db_session.query(Games)
        results2 = qry.all()
        print(len(results2))
        print(results)
        sent = "A mighty bad time is coming."
        print(re.split('[-_;:?<>() |, |/*|\n.!-+\t]', sent.lower()).count('bad'))
        print(re.split('[-_;:?<>() |, |/*|\n.!-+\t]', sent.lower()))
        print(results[0].AboutText)
        postsplit = re.split('[-_;:?<>() |, |/*|\n.!-+\t]', results[0].AboutText.lower())
        countplusblanks = len(postsplit)
        numofblanks = postsplit.count('')
        print(re.split(r'[-_;:?<>() |, |/*|\n.!-+\t]', results[0].AboutText.lower()))
        while postsplit.count(''):
            postsplit.remove('')
        print(postsplit)
        print(numofblanks)
        print(countplusblanks-numofblanks)
        print(results[0].tfidfScore)
        """

        results.sort(key=operator.attrgetter('tfidfScore'), reverse=True)

        return render_template('results.html', table=results)
        #table = Results(results)
        #table.border = True
        #return render_template('results.html', table=table)

if __name__ == '__main__':
    app.run(debug=True)
