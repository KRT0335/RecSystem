from flask_table import Col
from flask_table import Table

class Results(Table):
    id = Col('ID', show=False)
    QueryName = Col('QueryName')
    ReleaseDate = Col('ReleaseDate')
    Metacritic = Col('Metacritic')
    RecommendationCount = Col('RecommendationCount')
    PriceInitial = Col('PriceInitial')
    AboutText = Col('AboutText')

