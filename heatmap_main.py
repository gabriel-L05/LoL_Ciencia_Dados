import mysql.connector
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='LolData'
)

query = '''
SELECT kills, deaths, assists, gold_earned, total_damage, total_healing, minions_killed, penta_kills, quadra_kills, triple_kills
FROM player_stats
'''
df = pd.read_sql(query, conn)

corr_matrix = df.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Heatmap de Correlação entre Métricas dos Jogadores')
plt.show()

conn.close()
