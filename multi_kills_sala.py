import matplotlib.pyplot as plt
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',  
    user='root',
    password='', 
    database='LolData'
)
cursor = conn.cursor()

cursor.execute('''
    SELECT SUM(penta_kills), SUM(quadra_kills), SUM(triple_kills)
    FROM player_stats WHERE summoner_name IN ('Ahrice in Chains', 'Le0w20', 'BOBALHÃO123', 'costelão', 'mubarrigao', 'Pedrin1Minecraft', 'Lassengg');
''')

result = cursor.fetchone()

kills = ['Pentakills', 'Quadra Kills', 'Triple Kills']
counts = [result[0], result[1], result[2]]

plt.bar(kills, counts, color=['gold', 'purple', 'blue'])

plt.title('Número de Pentakills, Quadra Kills e Triple Kills')
plt.xlabel('Tipo de Kill')
plt.ylabel('Quantidade')

plt.show()

conn.close()

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",  
    user="root",      
    password="",      
    database="LolData" 
)
cursor = conn.cursor()

query = '''
    SELECT champion, SUM(penta_kills) AS penta_kills,
           SUM(quadra_kills) AS quadra_kills,
           SUM(triple_kills) AS triple_kills
    FROM player_stats 
    WHERE summoner_name IN ('Ahrice in Chains', 'Le0w20', 'BOBALHÃO123', 'costelão', 'mubarrigao', 'Pedrin1Minecraft', 'Lassengg')
    GROUP BY champion
    HAVING SUM(penta_kills) > 0 OR SUM(quadra_kills) > 0 OR SUM(triple_kills) > 0
    ORDER BY penta_kills DESC, quadra_kills DESC, triple_kills DESC
    LIMIT 50;
'''

cursor.execute(query)
data = cursor.fetchall()

df = pd.DataFrame(data, columns=["Champion", "Penta Kills", "Quadra Kills", "Triple Kills"])

df_penta = df.sort_values(by="Penta Kills", ascending=False).head(50)

plt.figure(figsize=(10, 6))
sns.barplot(data=df_penta, x="Champion", y="Penta Kills", palette="viridis")
plt.title('Top 50 Champions with Most Penta Kills')
plt.xticks(rotation=90)
plt.ylabel('Number of Penta Kills')
plt.tight_layout()
plt.show()

df_quadra = df.sort_values(by="Quadra Kills", ascending=False).head(50)

plt.figure(figsize=(10, 6))
sns.barplot(data=df_quadra, x="Champion", y="Quadra Kills", palette="Blues")
plt.title('Top 50 Champions with Most Quadra Kills')
plt.xticks(rotation=90)
plt.ylabel('Number of Quadra Kills')
plt.tight_layout()
plt.show()

df_triple = df.sort_values(by="Triple Kills", ascending=False).head(50)

plt.figure(figsize=(10, 6))
sns.barplot(data=df_triple, x="Champion", y="Triple Kills", palette="magma")
plt.title('Top 50 Champions with Most Triple Kills')
plt.xticks(rotation=90)
plt.ylabel('Number of Triple Kills')
plt.tight_layout()
plt.show()
