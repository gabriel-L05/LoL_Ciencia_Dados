import mysql.connector
import matplotlib.pyplot as plt
from collections import Counter

conn = mysql.connector.connect(
    host="localhost",      
    user="root",           
    password="",            
    database="LolData"     
)

cursor = conn.cursor()

cursor.execute("SELECT champion FROM player_stats")
champions_data = cursor.fetchall()

champions = [row[0] for row in champions_data]
champion_counts = Counter(champions)

top_champions = champion_counts.most_common(20)

labels = [champion[0] for champion in top_champions]
sizes = [champion[1] for champion in top_champions]
colors = plt.cm.Paired.colors[:len(labels)] 

plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
plt.title('Distribuição dos 20 Campeões Mais Escolhidos')

plt.show()

conn.close()
