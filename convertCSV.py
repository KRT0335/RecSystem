import csv
from flask1 import db
from flask1 import Games

db.create_all()



f = open('games-features.csv', encoding="utf8")

csv_f = csv.reader(f)

gf = []

#isSP=row[35]
#isMult=row[36]
#isIndie=row[44]

#isAction=row[45]
#isAdventure=row[46]
#isCasual=row[47]
#isStrategy=row[48]
#isRPG=row[49]
#isSim=row[50]

#isEarlyAccess=row[51]
#isF2P=row[52]
#isSports=row[53]
#isRacing=row[54]
#isMMO=row[55]

i = 0
for row in csv_f:
    if i == 0:
        i = 1
    else:
        i = i + 1
        db.session.add(Games(id = i, QueryName=row[2], ReleaseDate=row[4], Metacritic=row[9], RecommendationCount=row[12], isAction=row[45], isAdventure=row[46], isStrategy=row[48], isRPG=row[49], isSports=row[53], isRacing=row[54], PriceInitial=row[57], AboutText=row[61]))

db.session.commit()
f.close()

print(Games.query.get(1))
#print(Games.query.filter(Games.AboutText.contains('massive')))
#results = Games.query.filter(Games.QueryName.contains('massive'))
#for result in results:
    #print(result.id)
