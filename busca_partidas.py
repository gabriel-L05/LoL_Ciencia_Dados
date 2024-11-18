import requests
import mysql.connector
from mysql.connector import Error

# Configurações da API
API_KEY = 'RGAPI-0d0866c8-125d-4727-a238-e3019ff10bb9'

# Função para obter o puuid do jogador
def get_summoner_puuid(summoner_name, region, tag):
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}?api_key={API_KEY}'
          # https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/6481?api_key=RGAPI-0d0866c8-125d-4727-a238-e3019ff10bb9

    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('puuid')
    else:
        print(f'Erro ao obter puuid: {response.status_code} - {response.text}')
        return None
    

# Função para obter o histórico de partidas
def get_match_history(puuid, region, count=30):
    match_region = {
        'br1': 'americas',
        'na1': 'americas',
        'euw1': 'europe',
        'eun1': 'europe',
        'kr': 'asia',
        'jp1': 'asia',
        'oc1': 'sea',
        'la1': 'americas',
        'la2': 'americas',
        'ru': 'europe',
        'tr1': 'europe'
    }
    match_region = match_region.get(region, 'americas')
    url = f'https://{match_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}'
    headers = {'X-Riot-Token': API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Erro ao obter histórico de partidas: {response.status_code} - {response.text}')
        return []

# Função para obter detalhes de uma partida
def get_match_details(match_id, region):
    match_region = {
        'br1': 'americas',
        'na1': 'americas',
        'euw1': 'europe',
        'eun1': 'europe',
        'kr': 'asia',
        'jp1': 'asia',
        'oc1': 'sea',
        'la1': 'americas',
        'la2': 'americas',
        'ru': 'europe',
        'tr1': 'europe'
    }
    match_region = match_region.get(region, 'americas')
    url = f'https://{match_region}.api.riotgames.com/lol/match/v5/matches/{match_id}'
    headers = {'X-Riot-Token': API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def insert_match_details(connection, puuid, summoner_name, region, match_data):
    try:
        cursor = connection.cursor()
        participants = match_data['info']['participants']
        game_duration = match_data['info']['gameDuration']
        game_mode = match_data['info']['gameMode']
        game_type = match_data['info']['gameType']
        timestamp = match_data['info']['gameStartTimestamp']
        match_id = match_data['metadata']['matchId']
        
        # Loop através dos participantes para encontrar o jogador correto
        for participant in participants:
            if participant['puuid'] == puuid:
                # Montar os valores
                values = (
                    puuid,
                    summoner_name,
                    region,
                    match_id,
                    participant.get('championName', ''),
                    participant.get('championId', 0),
                    participant.get('summoner1Id', 0),
                    participant.get('summoner2Id', 0),
                    participant['perks']['styles'][0].get('style', 0),
                    participant['perks']['styles'][1].get('style', 0),
                    participant.get('kills', 0),
                    participant.get('deaths', 0),
                    participant.get('assists', 0),
                    participant.get('largestKillingSpree', 0),
                    participant.get('totalDamageDealtToChampions', 0),
                    participant.get('totalDamageTaken', 0),
                    participant.get('visionScore', 0),
                    participant.get('wardsPlaced', 0),
                    participant.get('wardsKilled', 0),
                    participant.get('goldEarned', 0),
                    participant.get('goldSpent', 0),
                    participant.get('item0', 0),
                    participant.get('item1', 0),
                    participant.get('item2', 0),
                    participant.get('item3', 0),
                    participant.get('item4', 0),
                    participant.get('item5', 0),
                    participant.get('item6', 0),
                    participant.get('totalMinionsKilled', 0),
                    participant.get('neutralMinionsKilled', 0),
                    participant.get('teamPosition', '') or '',
                    int(participant.get('win', False)),  # Converter booleano para inteiro
                    game_duration,
                    game_mode,
                    game_type,
                    timestamp
                )

                # Ajustar a consulta SQL
                query = '''
                    INSERT INTO match_details (
                        puuid, summoner_name, region, match_id, champion_name, champion_id, spell1_id, spell2_id,
                        perk_primary_style, perk_sub_style, kills, deaths, assists, largest_killing_spree, total_damage_dealt,
                        total_damage_taken, vision_score, wards_placed, wards_killed, gold_earned, gold_spent,
                        item0, item1, item2, item3, item4, item5, item6, total_minions_killed, neutral_minions_killed,
                        team_position, win, game_duration, game_mode, game_type, game_start_timestamp
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                '''

                # Imprimir consulta e valores para depuração
                print(f"Consulta SQL:\n{query}")
                print("Valores para inserir:", values)
                print("Número de valores:", len(values))

                # Inserir os dados no banco de dados
                cursor.execute(query, values)
        
        # Confirmar transação
        connection.commit()

    except Error as e:
        print(f"Erro ao inserir detalhes da partida: {e}")
    finally:
        cursor.close()


# Função principal
def fetch_and_store_matches(player_list):

        for player in player_list:
            summoner_name = player['name']
            region = player['region']
            tag = player['tag']
            puuid = get_summoner_puuid(summoner_name, region, tag)
            if puuid:
                match_ids = get_match_history(puuid, region)
                print(match_ids)
                # for match_id in match_ids:
                #     match_data = get_match_details(match_id, region)
                #     if match_data:
                        

# Exemplo de uso:
players = [{'name': 'paiN TitaN 10', 'region': 'americas', 'tag': 'xsqdl'}]
fetch_and_store_matches(players)
print("Processo concluído.")
