import mysql.connector
import matplotlib.pyplot as plt
from collections import Counter

# Conectar ao banco de dados MySQL
conn = mysql.connector.connect(
    host="localhost",       # ou o endereço do seu servidor
    user="root",            # usuário do banco
    password="",            # senha vazia
    database="LolData"      # nome do banco de dados
)

cursor = conn.cursor()

# Consultar todos os campeões escolhidos nas partidas
cursor.execute("SELECT champion FROM player_stats WHERE summoner_name IN ('Ahrice in Chains', 'Le0w20', 'BOBALHÃO123', 'costelão', 'mubarrigao', 'Pedrin1Minecraft', 'Lassengg');")
champions_data = cursor.fetchall()

# Contar a frequência de cada campeão
champions = [row[0] for row in champions_data]
champion_counts = Counter(champions)

# Selecionar os 10 campeões mais escolhidos
top_champions = champion_counts.most_common(50)

# Dados para o gráfico de pizza
labels = [champion[0] for champion in top_champions]
sizes = [champion[1] for champion in top_champions]
colors = plt.cm.Paired.colors[:len(labels)]  # Gera cores distintas para as fatias

# Criar o gráfico de pizza
plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
plt.title('Distribuição dos 10 Campeões Mais Escolhidos')

# Exibir o gráfico
plt.show()

# Fechar a conexão com o banco de dados
conn.close()
