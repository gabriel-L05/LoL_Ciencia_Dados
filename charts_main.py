import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
    
    # Ordenar pela soma total de kills (vitórias + derrotas)
    kills_df['total_kills'] = kills_df.sum(axis=1)
    kills_df = kills_df.sort_values(by='total_kills', ascending=False).head(50)
    
    # Plotar gráfico
    kills_df.drop(columns='total_kills').plot(kind='bar', stacked=True, color=['red', 'green'], figsize=(10, 6))
    plt.title('Kills por Campeão (Vitórias/Derrotas) - Top 50')
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


def plot_champion_winrates(players_df, min_games=15):
    # Calcular o total de partidas jogadas e o winrate por campeão
    champion_stats = players_df.groupby('champion').agg(
        total_games=('win', 'count'),
        winrate=('win', 'mean')
    )
    
    # Filtrar campeões com menos de 'min_games' partidas
    champion_stats = champion_stats[champion_stats['total_games'] >= min_games]
    
    # Ordenar campeões por winrate em ordem decrescente
    champion_stats = champion_stats.sort_values(by='winrate', ascending=False)
    
    top30_winrate = champion_stats.head(30)
    
    # Plotar gráfico de barras
    plt.figure(figsize=(20, 6))
    bars = plt.bar(top30_winrate.index, top30_winrate['winrate'], color='green')
    
    # Adicionar a quantidade de jogos como label em cada barra
    for bar, champion, total_games in zip(bars, top30_winrate.index, top30_winrate['total_games']):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, 
                 f'{total_games}', ha='center', va='bottom', fontsize=10)
    
    plt.title(f'Top 30 Campeões com Melhores Winrates e quantidade de jogos (Mais de {min_games} Partidas)')
    plt.xlabel('Campeão')
    plt.ylabel('Winrate')
    plt.xticks(rotation=45)
    plt.ylim(0, 1)  # Definir limite de y para representar winrate (0 a 1)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def best_champion_by_player(players_df, min_games=5):
    # Calcular o winrate por jogador e campeão
    player_champion_stats = players_df.groupby(['summoner_name',]).agg(
        total_games=('win', 'count'),
        winrate=('win', 'mean')
    ).reset_index()
    
    # Filtrar campeões com menos de 'min_games' partidas por jogador
    player_champion_stats = player_champion_stats[player_champion_stats['total_games'] >= min_games]
    
    # Determinar o campeão com o melhor winrate para cada jogador
    best_champions = player_champion_stats.loc[
        player_champion_stats.groupby('summoner_name')['winrate'].idxmax()
    ]
    
    # Ordenar por winrate em ordem decrescente para melhor visualização
    best_champions = best_champions.sort_values(by='winrate', ascending=False)
    
    # Exibir a tabela
    return best_champions[['summoner_name', 'champion', 'winrate', 'total_games']]


def plot_kda_by_champion(players_df, min_games=10):

    # Filtrar campeões com pelo menos 'min_games' partidas
    kda_stats = players_df.groupby('champion').agg(
        total_games=('win', 'count'),
        avg_kills=('kills', 'mean'),
        avg_deaths=('deaths', 'mean'),
        avg_assists=('assists', 'mean')
    ).reset_index()
    
    kda_stats = kda_stats[kda_stats['total_games'] >= min_games]
    
    # Ordenar por média de kills
    kda_stats = kda_stats.sort_values(by='avg_kills', ascending=False).head(10)

    # Gráfico de barras empilhadas
    plt.figure(figsize=(12, 6))
    plt.bar(kda_stats['champion'], kda_stats['avg_kills'], label='Kills', color='red')
    plt.bar(kda_stats['champion'], kda_stats['avg_deaths'], label='Deaths', color='gray', bottom=kda_stats['avg_kills'])
    plt.bar(kda_stats['champion'], kda_stats['avg_assists'], label='Assists', color='blue', bottom=kda_stats['avg_kills'] + kda_stats['avg_deaths'])

    plt.xlabel('Campeão')
    plt.ylabel('Média por Partida')
    plt.title('Média de Kills, Deaths e Assists por Campeão (Top 10)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def plot_game_duration_histogram(matches_df):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.hist(matches_df['game_duration'] / 60, bins=15, color='orange', edgecolor='black')
    plt.title('Distribuição da Duração das Partidas (em Minutos)')
    plt.xlabel('Duração (Minutos)')
    plt.ylabel('Número de Partidas')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

import matplotlib.pyplot as plt
import pandas as pd

def plot_matches_by_region(matches_df):
    # Criar uma nova coluna "region" com base na inicial do match_id (exemplo: 'KR', 'BR')
    matches_df['region'] = matches_df['match_id'].str[:2]  # Assume que a região está nas duas primeiras letras do ID
    
    # Contar o número de partidas por região
    region_counts = matches_df['region'].value_counts()

    # Plotando o gráfico de barras
    plt.figure(figsize=(10, 6))
    region_counts.plot(kind='bar', color='lightcoral')
    
    # Adicionando título e rótulos
    plt.title('Número de Partidas por Região')
    plt.xlabel('Região')
    plt.ylabel('Número de Partidas')
    
    # Exibindo o gráfico
    plt.xticks(rotation=45)
    plt.show()


# Chama a função para gerar o gráfico
# plot_matches_by_region(matches_df)
# plot_kda_by_champion(players_df)
# plot_game_duration_histogram(matches_df)
# plot_win_by_side(matches_df)
# plot_kills_by_champion(players_df)
# plot_gold_vs_damage(players_df)
plot_champion_winrates(players_df)

# best_champions_table = best_champion_by_player(players_df)
# print(best_champions_table)