from flask_table import Table, Col, LinkCol

class Results(Table):
    id = Col('ID', show=False)
    QueryName = Col('QueryName')
    ReleaseDate = Col('ReleaseDate')
    Metacritic = Col('Metacritic')
    RecommendationCount = Col('RecommendationCount')
    PriceInitial = Col('PriceInitial')
    AboutText = Col('AboutText')
