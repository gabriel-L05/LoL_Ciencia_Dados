import pymysql
import requests
import json

# Configurações do banco de dados
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "LolData"
}

# Função para conectar ao banco de dados MySQL
def connect_db():
    return pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# Função para criar tabelas (se não existirem)
def create_tables(connection):
    with connection.cursor() as cursor:
        # Tabela para informações da partida
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS match_info (
                match_id VARCHAR(50) PRIMARY KEY,
                game_duration INT,
                game_mode VARCHAR(50)
            )
        """)

        # Tabela para informações dos jogadores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id INT AUTO_INCREMENT PRIMARY KEY,
                match_id VARCHAR(50),
                summoner_name VARCHAR(50),
                champion_name VARCHAR(50),
                kills INT,
                deaths INT,
                assists INT,
                total_damage_dealt INT,
                gold_earned INT,
                vision_score INT,
                wards_placed INT,
                wards_killed INT,
                total_time_cc INT,
                team_position VARCHAR(10),
                FOREIGN KEY (match_id) REFERENCES match_info(match_id)
            )
        """)

        # Tabela para informações dos times
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_stats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                match_id VARCHAR(50),
                team_id INT,
                win BOOLEAN,
                dragons_killed INT,
                barons_killed INT,
                towers_killed INT,
                FOREIGN KEY (match_id) REFERENCES match_info(match_id)
            )
        """)

        connection.commit()

# Função para salvar os dados no banco de dados
def save_match_data(match_data, connection):
    with connection.cursor() as cursor:
        match_id = match_data["metadata"]["matchId"]
        game_duration = match_data["info"]["gameDuration"]
        game_mode = match_data["info"]["gameMode"]

        # Insere informações da partida
        cursor.execute("""
            INSERT IGNORE INTO match_info (match_id, game_duration, game_mode)
            VALUES (%s, %s, %s)
        """, (match_id, game_duration, game_mode))

        # Insere informações dos jogadores
        for participant in match_data["info"]["participants"]:
            cursor.execute("""
                INSERT INTO participants (
                    match_id, summoner_name, champion_name, kills, deaths, assists,
                    total_damage_dealt, gold_earned, vision_score, wards_placed,
                    wards_killed, total_time_cc, team_position
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                match_id, participant["summonerName"], participant["championName"],
                participant["kills"], participant["deaths"], participant["assists"],
                participant["totalDamageDealtToChampions"], participant["goldEarned"],
                participant["visionScore"], participant["wardsPlaced"],
                participant["wardsKilled"], participant["totalTimeCCDealt"],
                participant["teamPosition"]
            ))

        # Insere informações das equipes
        for team in match_data["info"]["teams"]:
            cursor.execute("""
                INSERT INTO team_stats (match_id, team_id, win, dragons_killed, barons_killed, towers_killed)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                match_id, team["teamId"], team["win"],
                team["objectives"]["dragon"]["kills"],
                team["objectives"]["baron"]["kills"],
                team["objectives"]["tower"]["kills"]
            ))

        connection.commit()

# Função principal para obter dados da partida e salvar no banco de dados
def fetch_and_save_match_data(api_token):
    match_id = "BR1_2970146077" 
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key=" + api_token
    response = requests.get(url)

    if response.status_code == 200:
        match_data = response.json()
        connection = connect_db()
        save_match_data(match_data, connection)
        connection.close()
        print("Dados salvos com sucesso no banco de dados!")
    else:
        print(f"Erro ao obter dados: {response.status_code} - {response.text}")

# Exemplo de uso
if __name__ == "__main__":
    api_token = "RGAPI-68a58d02-3ffe-45c6-9730-80db4a20eb98"
    fetch_and_save_match_data(api_token)