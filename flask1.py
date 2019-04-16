from flask import Flask, render_template, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from db_setup import init_db, db_session
from forms import GameSearchForm, ClassifierForm
import numpy as np
import re
import operator
import math

#pip install flask
#pip install flask-wtf
#pip install flask-sqlalchemy
#pip install flask_table

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
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
    isAction = db.Column(db.String(8), nullable=False)
    isAdventure = db.Column(db.String(8), nullable=False)
    isStrategy = db.Column(db.String(8), nullable=False)
    isRPG = db.Column(db.String(8), nullable=False)
    isSports = db.Column(db.String(8), nullable=False)
    isRacing = db.Column(db.String(8), nullable=False)
    tfidfScore = 0.0

    def __init__(self, id, QueryName, ReleaseDate, Metacritic, RecommendationCount, PriceInitial, AboutText, isAction, isAdventure, isStrategy, isRPG, isSports, isRacing):
        self.id = id
        self.QueryName = QueryName
        self.ReleaseDate = ReleaseDate
        self.Metacritic = Metacritic
        self.RecommendationCount = RecommendationCount
        self.PriceInitial = PriceInitial
        self.AboutText = AboutText
        self.isAction = isAction
        self.isAdventure = isAdventure
        self.isStrategy = isStrategy
        self.isRPG = isRPG
        self.isSports = isSports
        self.isRacing = isRacing
        self.tfidfScore = 0.0

    def __iter__(self):
        return self
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

@app.route('/classifierIndex', methods=['GET', 'POST'])
def class_index():
    query = ClassifierForm(request.form)
    if request.method == 'POST':
        return class_results(query)
    return render_template('classifierIndex.html', form=query)

@app.route('/classifier', methods=['GET', 'POST'])
def class_results(query):
    query = ClassifierForm(request.form)
    query_string = query.data['query']
    query_string_vector = re.split('[-_;:?<>() |, |/*|\n.!-+\t]', query_string.lower())
    while query_string_vector.count(''):
        query_string_vector.remove('')
    query_string_vector_unique = np.unique(query_string_vector).tolist()
    query_string_num = len(query_string_vector_unique)

    qry = db_session.query(Games)
    results = qry.all()

    numofDoc = len(results)

    #Get num of unique words over every document
    bag = []
    bagAction = []
    bagAdventure = []
    bagStrategy = []
    bagRPG = []
    bagSport = []
    bagRacing = []
    numAction = 0
    numAdventure = 0
    numStrategy = 0
    numRPG = 0
    numSports = 0
    numRacing = 0
    P_class_given_d = np.zeros(6).tolist()
    probArray = np.zeros((6, query_string_num)).tolist()
    #1: Action
    #2: Adventure
    #3: Strategy
    #4: RPG
    #5: Sports
    #6: Racing
    for i in range(0, numofDoc):
        string_vector = re.split('[-_;:?<>() |, |/*|\n.!-+\t]', results[i].AboutText.lower())
        while string_vector.count(''):
            string_vector.remove('')
        string_vector_unique = np.unique(string_vector).tolist()

        # Class Distribution
        if results[i].isAction == 'True':
            numAction = numAction + 1
            bagAction.extend(string_vector)
        if results[i].isAdventure == 'True':
            numAdventure = numAdventure + 1
            bagAdventure.extend(string_vector)
        if results[i].isStrategy == 'True':
            numStrategy = numStrategy + 1
            bagStrategy.extend(string_vector)
        if results[i].isRPG == 'True':
            numRPG = numRPG + 1
            bagRPG.extend(string_vector)
        if results[i].isSports == 'True':
            numSports = numSports + 1
            bagSport.extend(string_vector)
        if results[i].isRacing == 'True':
            numRacing = numRacing + 1
            bagRacing.extend(string_vector)

        bag.extend(string_vector_unique)



    numWordsAction = len(bagAction)
    numWordsAdventure = len(bagAdventure)
    numWordsStrategy = len(bagStrategy)
    numWordsRPG = len(bagRPG)
    numWordsSport = len(bagSport)
    numWordsRacing = len(bagRacing)

    numUniqueWords = len(set(bag))

    for j in range(query_string_num):
        #P(word | class) = (num of times "word" shows up in "class" + 1)/(total num of words in "class" + num of unique words over all of the documents)
        probArray[0][j] = (bagAction.count(query_string_vector_unique[j]) + 1)/(numWordsAction + numUniqueWords)
        probArray[1][j] = (bagAdventure.count(query_string_vector_unique[j]) + 1)/(numWordsAdventure + numUniqueWords)
        probArray[2][j] = (bagStrategy.count(query_string_vector_unique[j]) + 1)/(numWordsStrategy + numUniqueWords)
        probArray[3][j] = (bagRPG.count(query_string_vector_unique[j]) + 1)/(numWordsRPG + numUniqueWords)
        probArray[4][j] = (bagSport.count(query_string_vector_unique[j]) + 1)/(numWordsSport + numUniqueWords)
        probArray[5][j] = (bagRacing.count(query_string_vector_unique[j]) + 1)/(numWordsRacing + numUniqueWords)

    #P(isAction)
    P_Action = numAction/numofDoc
    #P(isAdventure)
    P_Adventure = numAdventure/numofDoc
    #P(isStrategy)
    P_Strategy = numStrategy/numofDoc
    #P(isRPG)
    P_RPG = numRPG/numofDoc
    #P(isSports)
    P_Sports = numSports/numofDoc
    #P(isRacing)
    P_Racing = numRacing/numofDoc

    P_class_given_d[0] = P_Action
    P_class_given_d[1] = P_Adventure
    P_class_given_d[2] = P_Strategy
    P_class_given_d[3] = P_RPG
    P_class_given_d[4] = P_Sports
    P_class_given_d[5] = P_Racing

    for k in range(query_string_num):
        for l in range(query_string_vector.count(query_string_vector_unique[k])):
            P_class_given_d[0] = P_class_given_d[0] * probArray[0][k]
            P_class_given_d[1] = P_class_given_d[1] * probArray[1][k]
            P_class_given_d[2] = P_class_given_d[2] * probArray[2][k]
            P_class_given_d[3] = P_class_given_d[3] * probArray[3][k]
            P_class_given_d[4] = P_class_given_d[4] * probArray[4][k]
            P_class_given_d[5] = P_class_given_d[5] * probArray[5][k]



    return render_template('classifier.html', form=query, query_string_vector_unique=query_string_vector_unique, query_string_num=query_string_num, P_Action=P_Action, P_Adventure=P_Adventure, P_Strategy=P_Strategy, P_RPG=P_RPG, P_Sports=P_Sports, P_Racing=P_Racing, numWordsAction=numWordsAction, numWordsAdventure=numWordsAdventure, numWordsStrategy=numWordsStrategy, numWordsRPG=numWordsRPG, numWordsSport=numWordsSport, numWordsRacing=numWordsRacing, numUniqueWords=numUniqueWords, probArray=probArray, P_class_given_d=P_class_given_d)


@app.route('/results', methods=['GET', 'POST'])
def search_results(search):
    search = GameSearchForm(request.form)
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

    results.sort(key=operator.attrgetter('tfidfScore'), reverse=True)

    if results[0].tfidfScore == 0.0:
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

        #results.sort(key=operator.attrgetter('tfidfScore'), reverse=True)
        maxDisp = 10
        for i in range(0, maxDisp):
            if results[i].tfidfScore == 0.0 and maxDisp == 10:
                maxDisp = i
                print(maxDisp)


        return render_template('results.html', table=results[0:maxDisp], form=search)
        #table = Results(results)
        #table.border = True
        #return render_template('results.html', table=table)

if __name__ == '__main__':
    app.run(debug=True)

"""
from flask import Flask, render_template, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from db_setup import init_db, db_session
from forms import GameSearchForm

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

    def __init__(self, QueryName, ReleaseDate, Metacritic, RecommendationCount, PriceInitial, AboutText):
        self.QueryName = QueryName
        self.ReleaseDate = ReleaseDate
        self.Metacritic = Metacritic
        self.RecommendationCount = RecommendationCount
        self.PriceInitial = PriceInitial
        self.AboutText = AboutText

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
    #return render_template('home.html')

@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search_string:
        if search.data['select'] == 'AboutText':
            qry = db_session.query(Games).filter(Games.AboutText.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'QueryName':
            qry = db_session.query(Games).filter(Games.QueryName.contains(search_string))
            results = qry.all()
        else:
            qry = db_session.query(Games)
            results = qry.all()
    else:
        qry = db_session.query(Games)
        results = qry.all()

    if not results:
        flash('No results found.')
        return redirect('/')
    else:
        #print(results[0].QueryName)
        return render_template('results.html', table=results)
        #table = Results(results)
        #table.border = True
        #return render_template('results.html', table=table)

if __name__ == '__main__':
    app.run(debug=True)


"""
