# Video Game Recommender System

Website: http://discorn.pythonanywhere.com/

# Hosting, Framework, Language
Hosting: PythonAnywhere  
Framework: Flask  
Languages: Python 3.6, SQLite, HTML, CSS  

# Using the code
After downloading all of the files  
App routing / main file: flask1.py  
Uses games.db (This was made for PythonAnywhere so **app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'** for localhost and **app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/<username>/mysite/games.db'** for PythonAnywhere) as the central database that was build using the dataset provided by Craig Kell under another program convertCSV.py to summarize the dataset to a more understandable database to be internally stored on the Games class in flask1.py.  
  




# Dataset: 
https://data.world/craigkelly/steam-game-data  
# References:
Basic flask tutorial  
http://www.blog.pythonlibrary.org/2017/12/12/flask-101-getting-started/  
Video tutorial of Python Flask by Corey Schafer  
https://www.youtube.com/watch?v=MwZwr5Tvyxo  
Blog describing TF-IDF integration into Python  
https://towardsdatascience.com/tf-idf-for-document-ranking-from-scratch-in-python-on-real-world-dataset-796d339a4089  
