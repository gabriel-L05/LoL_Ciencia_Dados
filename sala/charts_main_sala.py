import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

conn = mysql.connector.connect(
    host='localhost',     
    user='root',          
    password='',          
    database='LolData'     
)

def fetch_data():
    matches_query = "SELECT B.* FROM player_stats A INNER JOIN matches B ON A.match_id = B.match_id WHERE summoner_name IN ('Ahrice in Chains', 'Le0w20', 'BOBALHÃO123', 'costelão', 'mubarrigao', 'Pedrin1Minecraft', 'Lassengg');"
    players_query = "SELECT * FROM player_stats WHERE summoner_name IN ('Ahrice in Chains', 'Le0w20', 'BOBALHÃO123', 'costelão', 'mubarrigao', 'Pedrin1Minecraft', 'Lassengg');"
    
    matches_df = pd.read_sql(matches_query, conn)
    players_df = pd.read_sql(players_query, conn)
    
    return matches_df, players_df

matches_df, players_df = fetch_data()

def plot_win_by_side(matches_df):
    win_by_side = matches_df[['blue_side_win', 'red_side_win']].sum()
    labels = ['Blue Side Wins', 'Red Side Wins']
    
    plt.figure(figsize=(6, 4))
    plt.bar(labels, win_by_side, color=['blue', 'red'])
    plt.title('Vitórias por Lado')
    plt.ylabel('Número de Vitórias')
    plt.show()

def plot_kills_by_champion(players_df):
    players_df['win'] = players_df['win'].astype(int) 
    kills_df = players_df.groupby(['champion', 'win'])['kills'].sum().unstack().fillna(0)
    
    kills_df['total_kills'] = kills_df.sum(axis=1)
    kills_df = kills_df.sort_values(by='total_kills', ascending=False).head(50)
    
    kills_df.drop(columns='total_kills').plot(kind='bar', stacked=True, color=['red', 'green'], figsize=(10, 6))
    plt.title('Kills por Campeão (Vitórias/Derrotas) - Top 50')
    plt.ylabel('Total de Kills')
    plt.xlabel('Campeão')
    plt.xticks(rotation=90)
    plt.show()


def plot_gold_vs_damage(players_df):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=players_df, x='gold_earned', y='total_damage', hue='win', palette={0: 'red', 1: 'green'})
    plt.title('Correlação entre Ouro Ganhado e Dano Causado por Jogador')
    plt.xlabel('Ouro Ganhado')
    plt.ylabel('Dano Total')
    plt.legend(title='Vitória', labels=['Derrota', 'Vitória'])
    plt.show()

def plot_champion_winrates(players_df, min_games=15):
    champion_stats = players_df.groupby('champion').agg(
        total_games=('win', 'count'),
        winrate=('win', 'mean')
    )
    
    champion_stats = champion_stats[champion_stats['total_games'] >= min_games]
    
    champion_stats = champion_stats.sort_values(by='winrate', ascending=False)
    
    top30_winrate = champion_stats.head(30)
    
    plt.figure(figsize=(20, 6))
    bars = plt.bar(top30_winrate.index, top30_winrate['winrate'], color='green')
    
    for bar, champion, total_games in zip(bars, top30_winrate.index, top30_winrate['total_games']):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, 
                 f'{total_games}', ha='center', va='bottom', fontsize=10)
    
    plt.title(f'Top 30 Campeões com Melhores Winrates e quantidade de jogos (Mais de {min_games} Partidas)')
    plt.xlabel('Campeão')
    plt.ylabel('Winrate')
    plt.xticks(rotation=45)
    plt.ylim(0, 1)  
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def plot_kda_by_champion(players_df, min_games=10):

    kda_stats = players_df.groupby('champion').agg(
        total_games=('win', 'count'),
        avg_kills=('kills', 'mean'),
        avg_deaths=('deaths', 'mean'),
        avg_assists=('assists', 'mean')
    ).reset_index()
    
    kda_stats = kda_stats[kda_stats['total_games'] >= min_games]
    
    kda_stats = kda_stats.sort_values(by='avg_kills', ascending=False).head(10)

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


def plot_matches_by_region(matches_df):
    matches_df['region'] = matches_df['match_id'].str[:2] 
    
    region_counts = matches_df['region'].value_counts()

    plt.figure(figsize=(10, 6))
    region_counts.plot(kind='bar', color='lightcoral')
    
    plt.title('Número de Partidas por Região')
    plt.xlabel('Região')
    plt.ylabel('Número de Partidas')
    
    plt.xticks(rotation=45)
    plt.show()


plot_matches_by_region(matches_df)
plot_kda_by_champion(players_df)
plot_game_duration_histogram(matches_df)
plot_win_by_side(matches_df)
plot_kills_by_champion(players_df)
plot_gold_vs_damage(players_df)
plot_champion_winrates(players_df)
