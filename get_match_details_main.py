import requests
import mysql.connector
import time
from dotenv import load_dotenv
import os

# Carregar as variáveis do arquivo .env
load_dotenv()

# Acessar a chave de API

# Configurações
API_KEY = os.getenv('API_KEY')
# REGION = 'asia'
# BASE_URL = f'https://{REGION}.api.riotgames.com'
HEADERS = {'X-Riot-Token': API_KEY}

# Função para obter o PUUID a partir do Riot ID
def get_puuid_by_riot_id(game_name, tag_line, region):
    account_url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}'
    response = requests.get(account_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get('puuid')
    return None

# Função para obter o histórico de partidas do jogador
def get_summoner_matches(puuid, region, count=30):
    match_url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}'
    matches = requests.get(match_url, headers=HEADERS).json()
    return matches

# Função para obter detalhes de uma partida
def get_match_details(match_id, region):
    match_detail_url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}'
    match_details = requests.get(match_detail_url, headers=HEADERS).json()
    return match_details

# Conectar ao banco de dados MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='LolData'
)
cursor = conn.cursor()

# Função para criar tabelas no banco de dados
def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            match_id VARCHAR(50) PRIMARY KEY,
            game_duration INT,
            game_mode VARCHAR(20),
            ranked BOOLEAN,
            blue_side_win BOOLEAN,
            red_side_win BOOLEAN,
            blue_dragons_killed INT,
            red_dragons_killed INT
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            match_id VARCHAR(50),
            player_id VARCHAR(50),
            summoner_name VARCHAR(50),
            team_id INT,
            champion VARCHAR(50),
            kills INT,
            deaths INT,
            assists INT,
            lane VARCHAR(20),
            role VARCHAR(20),
            vision_score INT,
            gold_earned INT,
            total_damage INT,
            total_healing INT,
            minions_killed INT,
            penta_kills INT,
            quadra_kills INT,
            triple_kills INT,
            allInPings INT,
            win BOOLEAN,
            PRIMARY KEY (match_id, player_id),
            FOREIGN KEY (match_id) REFERENCES matches(match_id)
        )''')
    conn.commit()

# Função para salvar dados da partida no banco de dados
def save_match_data(match_id, match_data):
    try:
        info = match_data['info']
        teams = info['teams']

        blue_side_win = teams[0]['win']
        red_side_win = teams[1]['win']
        blue_dragons = teams[0]['objectives']['dragon']['kills']
        red_dragons = teams[1]['objectives']['dragon']['kills']

        cursor.execute('''
            INSERT IGNORE INTO matches (match_id, game_duration, game_mode, ranked, 
                                        blue_side_win, red_side_win, 
                                        blue_dragons_killed, red_dragons_killed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                       (match_id, info['gameDuration'], info['gameMode'], info['gameType'] == 'RANKED',
                        blue_side_win, red_side_win, blue_dragons, red_dragons))

        for player in info['participants']:
            # Salvar estatísticas individuais dos jogadores
            cursor.execute('''
                INSERT IGNORE INTO player_stats 
                (match_id, player_id, summoner_name, team_id, champion, kills, deaths, assists, lane, role, vision_score, 
                 gold_earned, total_damage, total_healing, minions_killed, penta_kills, quadra_kills, 
                 triple_kills, allInPings, win) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (match_id, 
                            player['summonerId'], 
                            player['summonerName'],
                            player['teamId'], 
                            player['championName'], 
                            player['kills'], 
                            player['deaths'], 
                            player['assists'], 
                            player['lane'], 
                            player['role'], 
                            player['visionScore'], 
                            player['goldEarned'], 
                            player['totalDamageDealtToChampions'], 
                            player['totalHeal'], 
                            player['totalMinionsKilled'], 
                            player['pentaKills'], 
                            player['quadraKills'], 
                            player['tripleKills'], 
                            player['allInPings'], 
                            player['win']))
        conn.commit()
    except Exception as e:
        print(f'Erro ao salvar dados da partida {match_id}: {e}')

# Função principal para coletar e armazenar dados
def collect_and_store_data(game_name, tag_line, region, num_matches=30):
    create_tables()
    puuid = get_puuid_by_riot_id(game_name, tag_line, region)
    if puuid:
        matches = get_summoner_matches(puuid, region, count=num_matches)
        for match_id in matches:
            match_data = get_match_details(match_id, region)
            save_match_data(match_id, match_data)
            print('Dados salvos')
            time.sleep(1.2)  

# Executar o código

# Lista de jogadores, suas respectivas tags e regiões
players = [
    {"game_name": "Oner", "tag_line": "KR222", "region": "asia"},
    {"game_name": "Faker", "tag_line": "KR1", "region": "asia"},
    {"game_name": "T1 Gumayusi", "tag_line": "KR1", "region": "asia"},
    {"game_name": "Keria", "tag_line": "Ker10", "region": "asia"},
    {"game_name": "kiin", "tag_line": "KR1", "region": "asia"},
    {"game_name": "Canyon", "tag_line": "KR1", "region": "asia"},
    {"game_name": "Chovy", "tag_line": "0303", "region": "asia"},
    {"game_name": "Peyz", "tag_line": "KR11", "region": "asia"},
    {"game_name": "Lehends", "tag_line": "KR1", "region": "asia"},
    {"game_name": "Kingen", "tag_line": "KR1", "region": "asia"},
    {"game_name": "DK Lucid", "tag_line": "KR1", "region": "asia"},
    {"game_name": "DK ShowMaker", "tag_line": "KR1", "region": "asia"},
    {"game_name": "Aiming", "tag_line": "xxxx", "region": "asia"},
    {"game_name": "Doran", "tag_line": "KR1", "region": "asia"},
    {"game_name": "Peanut", "tag_line": "KR1", "region": "asia"},
    {"game_name": "Zeka", "tag_line": "1128", "region": "asia"},
    {"game_name": "Viper", "tag_line": "KR33", "region": "asia"},
    {"game_name": "Delight", "tag_line": "KR1", "region": "asia"}
]

# Função para coletar e armazenar dados
def pesquisa_por_nome(game_name, tag_line, region):
    print(f"Coletando dados para: {game_name}#{tag_line} na região {region}")
    
    collect_and_store_data(game_name, tag_line, region)

# Loop para percorrer todos os jogadores
for player in players:
    pesquisa_por_nome(player['game_name'], player['tag_line'], player['region'])

# Fechar conexão
cursor.close()
conn.close()

