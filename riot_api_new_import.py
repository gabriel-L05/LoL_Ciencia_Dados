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
REGION = 'americas'  # Mude para a região desejada
BASE_URL = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches'

match_ids = ['BR1_3019274124', 'BR1_3019271063', 'BR1_3013905488', 'BR1_3013896840', 'BR1_3010798709', 'BR1_3010207097', 'BR1_3009661644', 'BR1_3009307124', 'BR1_3009282682', 'BR1_3009025282', 'BR1_3008995888', 'BR1_3008969244', 'BR1_3008949502', 'BR1_3008932145', 'BR1_3008910574', 'BR1_3008898288', 'BR1_3008880065', 'BR1_3008860358', 'BR1_3008839325', 'BR1_3008827779', 'BR1_3008817572', 'BR1_2997385438', 'BR1_2997361490', 'BR1_2997342049', 'BR1_2997331299', 'BR1_2997314270', 'BR1_2997183558', 'BR1_2997165453', 'BR1_2996696661', 'BR1_2996281733']      

# Configurar o banco de dados MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='LolData'
)
cursor = conn.cursor()

# Criar tabelas no banco de dados
cursor.execute('''
CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR(50) PRIMARY KEY,
    game_duration INT,
    game_mode VARCHAR(50),
    game_type VARCHAR(50),
    win_team INT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS player_stats (
    match_id VARCHAR(50),
    summoner_name VARCHAR(100),
    champion_id INT,
    kills INT,
    deaths INT,
    assists INT,
    total_damage_dealt INT,
    total_damage_taken INT,
    gold_earned INT,
    cs_per_min FLOAT,
    wards_placed INT,
    wards_destroyed INT,
    PRIMARY KEY (match_id, summoner_name),
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
)
''')

conn.commit()

# Função para fazer requisição de uma partida
def get_match_details(match_id):
    url = f'{BASE_URL}/{match_id}?api_key=' + API_KEY

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Erro ao buscar detalhes da partida {match_id}: {response.status_code}')
        return None

# Função para salvar dados no banco de dados
def save_match_data(match_data):
    match_id = match_data['metadata']['matchId']
    game_duration = match_data['info']['gameDuration']
    game_mode = match_data['info']['gameMode']
    game_type = match_data['info']['gameType']

    # Verificar se a equipe vencedora é 100 ou 200
    win_team = next((team['teamId'] for team in match_data['info']['teams'] if team['win']), None)

    cursor.execute('''
    INSERT IGNORE INTO matches (match_id, game_duration, game_mode, game_type, win_team)
    VALUES (%s, %s, %s, %s, %s)
    ''', (match_id, game_duration, game_mode, game_type, win_team))

    for participant in match_data['info']['participants']:
        summoner_name = participant['summonerName']
        champion_id = participant['championId']
        kills = participant['kills']
        deaths = participant['deaths']
        assists = participant['assists']
        total_damage_dealt = participant['totalDamageDealtToChampions']
        total_damage_taken = participant['totalDamageTaken']
        gold_earned = participant['goldEarned']
        cs_per_min = (participant['totalMinionsKilled'] + participant['neutralMinionsKilled']) / (game_duration / 60)
        wards_placed = participant['wardsPlaced']
        wards_destroyed = participant['wardsKilled']

        cursor.execute('''
        INSERT IGNORE INTO player_stats (match_id, summoner_name, champion_id, kills, deaths, assists,
                                        total_damage_dealt, total_damage_taken, gold_earned, cs_per_min,
                                        wards_placed, wards_destroyed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (match_id, summoner_name, champion_id, kills, deaths, assists, total_damage_dealt,
              total_damage_taken, gold_earned, cs_per_min, wards_placed, wards_destroyed))
    print('Dados Salvos')
    conn.commit()

# Exemplo de uso: buscar detalhes de várias partidas e salvar

for match_id in match_ids:
    match_data = get_match_details(match_id)
    if match_data:
        save_match_data(match_data)
        time.sleep(1.2)  # Respeitar o rate limit da API

# Fechar a conexão do banco de dados
conn.close()
