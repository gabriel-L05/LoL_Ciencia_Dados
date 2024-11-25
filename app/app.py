from flask import Flask, render_template
from database import fetch_match_data, fetch_player_data
import plotly.graph_objs as go
import plotly
import json

app = Flask(__name__)

@app.route("/")
def index():
    matches = fetch_match_data()
    players = fetch_player_data()

    # Processa dados
    worst_win_rate_players = calculate_worst_win_rate(players)
    worst_champion_winrates = calculate_worst_champion_winrates(players)
    worst_kda_players = calculate_worst_kda(players)
    worst_matches = calculate_worst_matches(players)
    champion_winrates = calculate_most_played_champions(players)  # Campeões mais jogados e win rate
    death_ranking = calculate_death_ranking(players)
    lowest_damage_players = calculate_lowest_damage(players)

    return render_template(
        "index.html",
        worst_win_rate_players=worst_win_rate_players,
        worst_kda_players=worst_kda_players,
        worst_matches=worst_matches,
        champion_winrates=champion_winrates,  # Passando os campeões mais jogados e win rates para o template
        death_ranking=death_ranking,
        worst_champion_winrates=worst_champion_winrates, 
        lowest_damage_players=lowest_damage_players
    )



# Calcula os 10 piores jogadores por win rate
def calculate_worst_win_rate(players):
    from collections import defaultdict

    player_stats = defaultdict(lambda: {'wins': 0, 'games': 0})
    for player in players:
        player_stats[player['summoner_name']]['games'] += 1
        if player['win']:
            player_stats[player['summoner_name']]['wins'] += 1

    win_rates = [
        {'summoner_name': name, 'win_rate': stats['wins'] / stats['games'] * 100}
        for name, stats in player_stats.items()
    ]
    return sorted(win_rates, key=lambda x: x['win_rate'])[:10]

def calculate_worst_kda(players):
    def calculate_kda(player):
        deaths = player['deaths'] or 1  # Evita divisão por zero
        return (player['kills'] + player['assists']) / deaths

    player_kda = [
        {'summoner_name': player['summoner_name'], 'kda': calculate_kda(player)}
        for player in players
    ]

    
    return sorted(player_kda, key=lambda x: x['kda'])[:10]


# Calcula o gráfico das 10 piores partidas baseado nas mortes por jogador
def calculate_worst_matches(players):
    death_counts = {}
    for player in players:
        name = player['summoner_name']
        if name not in death_counts:
            death_counts[name] = 0
        death_counts[name] += player['deaths']

    worst_players = sorted(death_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    data = [go.Bar(x=[player[0] for player in worst_players], y=[player[1] for player in worst_players])]
    layout = go.Layout(title="Top 10 Piores Partidas (Baseado em Mortes)", xaxis=dict(title="Jogador"), yaxis=dict(title="Mortes"))
    return json.dumps(go.Figure(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder)

from collections import defaultdict

def calculate_most_played_champions(players):
    champion_stats = defaultdict(lambda: {'games_played': 0, 'wins': 0})

    for player in players:
        champion = player['champion']
        champion_stats[champion]['games_played'] += 1
        if player['win']:
            champion_stats[champion]['wins'] += 1

    # Calculando win rate para cada campeão
    champion_winrates = [
        {
            'champion': champion,
            'win_rate': stats['wins'] / stats['games_played'] * 100 if stats['games_played'] > 0 else 0,
            'games_played': stats['games_played']
        }
        for champion, stats in champion_stats.items()
    ]

    # Ordenando os campeões por número de jogos jogados (do maior para o menor)
    champion_winrates_sorted = sorted(champion_winrates, key=lambda x: x['games_played'], reverse=True)[:10]
    
    return champion_winrates_sorted

# Gráfico com as 10 piores win rates por campeão
def calculate_worst_champion_winrates(players):
    from collections import defaultdict

    champion_stats = defaultdict(lambda: {'wins': 0, 'games': 0})
    for player in players:
        champion_stats[player['champion']]['games'] += 1
        if player['win']:
            champion_stats[player['champion']]['wins'] += 1

    win_rates = [
        {'champion': champ, 'win_rate': stats['wins'] / stats['games'] * 100}
        for champ, stats in champion_stats.items()
    ]
    top_10 = sorted(win_rates, key=lambda x: x['win_rate'])[:10]

    data = [go.Bar(x=[entry['champion'] for entry in top_10], y=[entry['win_rate'] for entry in top_10])]
    layout = go.Layout(title="10 Piores Win Rates por Campeão", xaxis=dict(title="Campeões"), yaxis=dict(title="Win Rate (%)"))
    return json.dumps(go.Figure(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder)

# Ranking de jogadores com a maior quantidade de mortes em uma partida
def calculate_death_ranking(players):
    death_ranking = sorted(
        players,
        key=lambda x: x['deaths'],
        reverse=True
    )[:10]  # Top 10 jogadores
    return [
        {
            'summoner_name': player['summoner_name'],
            'champion': player['champion'],
            'kda': f"{player['kills']}/{player['deaths']}/{player['assists']}"
        }
        for player in death_ranking
    ]



# Ranking de Jogadores com Menor Dano Causado
def calculate_lowest_damage(players):
    damage_ranking = sorted(
        players,
        key=lambda x: x['total_damage'],  # Ordena por dano total, do menor para o maior
        reverse=False
    )[:10]  # Top 10 jogadores com menor dano
    return [
        {
            'summoner_name': player['summoner_name'],
            'champion': player['champion'],
            'total_damage': player['total_damage'],
            'kills_deaths_assists': f"{player['kills']}/{player['deaths']}/{player['assists']}"
        }
        for player in damage_ranking
    ]


if __name__ == "__main__":
    app.run(debug=True)
