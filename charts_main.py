import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Conectar ao banco de dados MySQL
conn = mysql.connector.connect(
    host='localhost',      # ou outro host, se necessário
    user='root',           # usuário root
    password='',           # senha vazia
    database='LolData'     # nome do banco de dados
)

# Função para extrair dados de matches e player_stats
def fetch_data():
    matches_query = "SELECT * FROM matches"
    players_query = "SELECT * FROM player_stats"
    
    matches_df = pd.read_sql(matches_query, conn)
    players_df = pd.read_sql(players_query, conn)
    
    return matches_df, players_df

# Carregar os dados
matches_df, players_df = fetch_data()

# 1. Gráfico de Vitórias por Lado (Blue Side vs Red Side)
def plot_win_by_side(matches_df):
    win_by_side = matches_df[['blue_side_win', 'red_side_win']].sum()
    labels = ['Blue Side Wins', 'Red Side Wins']
    
    plt.figure(figsize=(6, 4))
    plt.bar(labels, win_by_side, color=['blue', 'red'])
    plt.title('Vitórias por Lado')
    plt.ylabel('Número de Vitórias')
    plt.show()

# 2. Análise de kills por campeão e suas vitórias/derrotas
def plot_kills_by_champion(players_df):
    # Contar total de kills por campeão e se o jogador ganhou
    players_df['win'] = players_df['win'].astype(int)  # Converter boolean para int para soma
    kills_df = players_df.groupby(['champion', 'win'])['kills'].sum().unstack().fillna(0)
    
    kills_df.plot(kind='bar', stacked=True, color=['red', 'green'], figsize=(10, 6))
    plt.title('Kills por Campeão (Vitórias/Derrotas)')
    plt.ylabel('Total de Kills')
    plt.xlabel('Campeão')
    plt.xticks(rotation=90)
    plt.show()


# 4. Correlação entre ouro ganho e dano causado por cada jogador
def plot_gold_vs_damage(players_df):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=players_df, x='gold_earned', y='total_damage', hue='win', palette={0: 'red', 1: 'green'})
    plt.title('Correlação entre Ouro Ganhado e Dano Causado por Jogador')
    plt.xlabel('Ouro Ganhado')
    plt.ylabel('Dano Total')
    plt.legend(title='Vitória', labels=['Derrota', 'Vitória'])
    plt.show()

# 5. Ranking de campeões com melhores winrates
def plot_champion_winrates(players_df):
    # Calcular o winrate por campeão
    champion_winrate = players_df.groupby('champion')['win'].mean().sort_values(ascending=False)
    
    # Exibir top 10 campeões com melhores winrates
    champion_winrate.head(50).plot(kind='bar', color='green', figsize=(10, 6))
    plt.title('Top 10 Campeões com Melhores Winrates')
    plt.xlabel('Campeão')
    plt.ylabel('Winrate')
    plt.xticks(rotation=90)
    plt.show()

# Gerar gráficos
plot_win_by_side(matches_df)
plot_kills_by_champion(players_df)
plot_gold_vs_damage(players_df)
plot_champion_winrates(players_df)
