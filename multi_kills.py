import matplotlib.pyplot as plt
import mysql.connector

# Conectar ao banco de dados MySQL
conn = mysql.connector.connect(
    host='localhost',  # Altere se necessário
    user='root',
    password='',  # Senha vazia conforme especificado
    database='LolData'
)
cursor = conn.cursor()

# Consultar o número de pentakills, quadra kills e triple kills
cursor.execute('''
    SELECT SUM(penta_kills), SUM(quadra_kills), SUM(triple_kills)
    FROM player_stats
''')

result = cursor.fetchone()

# Dados para o gráfico
kills = ['Pentakills', 'Quadra Kills', 'Triple Kills']
counts = [result[0], result[1], result[2]]

# Criar gráfico de barras
plt.bar(kills, counts, color=['gold', 'purple', 'blue'])

# Adicionar título e rótulos
plt.title('Número de Pentakills, Quadra Kills e Triple Kills')
plt.xlabel('Tipo de Kill')
plt.ylabel('Quantidade')

# Exibir o gráfico
plt.show()

# Fechar a conexão
conn.close()

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import mysql.connector

# Conectando ao banco de dados
conn = mysql.connector.connect(
    host="localhost",  # Substitua pelo seu host
    user="root",       # Substitua pelo seu usuário
    password="",       # Substitua pela sua senha
    database="LolData" # Substitua pelo nome do seu banco de dados
)
cursor = conn.cursor()

# Consultar dados de penta, quadra e triple kills, ignorando 0 e limitando a 50
query = '''
    SELECT champion, SUM(penta_kills) AS penta_kills,
           SUM(quadra_kills) AS quadra_kills,
           SUM(triple_kills) AS triple_kills
    FROM player_stats
    GROUP BY champion
    HAVING SUM(penta_kills) > 0 OR SUM(quadra_kills) > 0 OR SUM(triple_kills) > 0
    ORDER BY penta_kills DESC, quadra_kills DESC, triple_kills DESC
    LIMIT 50;
'''

cursor.execute(query)
data = cursor.fetchall()

# Criando DataFrame para visualização
df = pd.DataFrame(data, columns=["Champion", "Penta Kills", "Quadra Kills", "Triple Kills"])

# Gráfico de Penta Kills
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x="Champion", y="Penta Kills", palette="viridis")
plt.title('Top 50 Champions with Most Penta Kills')
plt.xticks(rotation=90)
plt.ylabel('Number of Penta Kills')
plt.tight_layout()
plt.show()

# Gráfico de Quadra Kills
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x="Champion", y="Quadra Kills", palette="Blues")
plt.title('Top 50 Champions with Most Quadra Kills')
plt.xticks(rotation=90)
plt.ylabel('Number of Quadra Kills')
plt.tight_layout()
plt.show()

# Gráfico de Triple Kills
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x="Champion", y="Triple Kills", palette="magma")
plt.title('Top 50 Champions with Most Triple Kills')
plt.xticks(rotation=90)
plt.ylabel('Number of Triple Kills')
plt.tight_layout()
plt.show()
