import mysql.connector
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Conectar ao banco de dados MySQL diretamente
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='LolData'
)

# Consultar as métricas de interesse da tabela player_stats
query = '''
SELECT kills, deaths, assists, gold_earned, total_damage, total_healing, minions_killed, penta_kills, quadra_kills, triple_kills
FROM player_stats
'''
# Usar pandas para executar a query e carregar os dados
df = pd.read_sql(query, conn)

# Calcular a correlação entre as colunas numéricas
corr_matrix = df.corr()

# Criar o heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Heatmap de Correlação entre Métricas dos Jogadores')
plt.show()

# Fechar a conexão com o banco de dados
conn.close()
