from flask import Flask, render_template
from database import  fetch_player_data
import plotly.graph_objs as go
import plotly
import json
from collections import defaultdict

app = Flask(__name__)

@app.route("/")
def index():
    players = fetch_player_data()

    worst_win_rate_players = calculate_worst_win_rate(players)
    worst_kda_players = calculate_worst_kda(players)
    worst_matches = calculate_worst_matches(players)
    champion_winrates = calculate_most_played_champions(players) 
    death_ranking = calculate_death_ranking(players)
    lowest_damage_players = calculate_lowest_damage(players)

    return render_template(
        "index.html",
        worst_win_rate_players=worst_win_rate_players,
        worst_kda_players=worst_kda_players,
        worst_matches=worst_matches,
        champion_winrates=champion_winrates,  
        death_ranking=death_ranking,
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
        deaths = player['deaths'] or 1  
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


def calculate_most_played_champions(players):
    champion_stats = defaultdict(lambda: {'games_played': 0, 'wins': 0})

    for player in players:
        champion = player['champion']
        champion_stats[champion]['games_played'] += 1
        if player['win']:
            champion_stats[champion]['wins'] += 1

    champion_winrates = [
        {
            'champion': champion,
            'win_rate': stats['wins'] / stats['games_played'] * 100 if stats['games_played'] > 0 else 0,
            'games_played': stats['games_played']
        }
        for champion, stats in champion_stats.items()
    ]

    champion_winrates_sorted = sorted(champion_winrates, key=lambda x: x['games_played'], reverse=True)[:10]
    
    return champion_winrates_sorted

# Ranking de jogadores com a maior quantidade de mortes em uma partida
def calculate_death_ranking(players):
    death_ranking = sorted(
        players,
        key=lambda x: x['deaths'],
        reverse=True
    )[:10]  
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
        key=lambda x: x['total_damage'],  
        reverse=False
    )[:10]  
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
