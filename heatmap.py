import mysql.connector
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Conectar ao banco de dados
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # senha vazia
    database="LolData"
)

cursor = conn.cursor()

# Consultar as informações de partidas e estatísticas de jogadores
query = '''
SELECT
    m.match_id,
    m.game_duration,
    m.blue_side_win,
    m.red_side_win,
    m.blue_dragons_killed,
    m.red_dragons_killed,
    ps.summoner_name,
    ps.team_id,
    ps.kills,
    ps.deaths,
    ps.assists,
    ps.vision_score,
    ps.gold_earned,
    ps.total_damage
FROM
    matches m
JOIN
    player_stats ps ON m.match_id = ps.match_id
'''

cursor.execute(query)
rows = cursor.fetchall()

# Converter para DataFrame do Pandas
df = pd.DataFrame(rows, columns=[
    'match_id', 'game_duration', 'blue_side_win', 'red_side_win', 
    'blue_dragons_killed', 'red_dragons_killed', 'summoner_name', 'team_id', 
    'kills', 'deaths', 'assists', 'vision_score', 'gold_earned', 'total_damage'
])

# Calcular KDA e adicionar no DataFrame
df['KDA'] = (df['kills'] + df['assists']) / df['deaths'].replace(0, 1)  # Evitar divisão por zero

# Agrupar as informações por partida e por time
df['side'] = df['team_id'].apply(lambda x: 'Blue' if x == 100 else 'Red')  # Time 100 é Blue, 200 é Red
df['win'] = df.apply(lambda row: row['blue_side_win'] if row['side'] == 'Blue' else row['red_side_win'], axis=1)

# Selecionar as colunas para o heatmap
heatmap_data = df[['game_duration', 'blue_dragons_killed', 'red_dragons_killed', 'kills', 'deaths', 'assists', 
                   'vision_score', 'gold_earned', 'total_damage', 'KDA', 'win']]

# Adicionar as condições de vitória para cada time
heatmap_data['side_win'] = heatmap_data['win'].apply(lambda x: 1 if x else 0)

# Criar o gráfico heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data.corr(), annot=True, cmap='coolwarm', linewidths=0.5)
plt.title("Comparação das Métricas de Partida e Jogadores")
plt.show()

# Fechar a conexão
cursor.close()
conn.close()
