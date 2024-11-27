import mysql.connector

# Configuração do banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'LolData'
}

def fetch_player_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # query = "SELECT A.* FROM player_stats A INNER JOIN matches B ON A.match_id = B.match_id WHERE summoner_name != ''"
    query = "SELECT A.* FROM player_stats A INNER JOIN matches B ON A.match_id = B.match_id WHERE summoner_name IN ('Ahrice in Chains', 'Le0w20', 'BOBALHÃO123', 'costelão', 'mubarrigao', 'Pedrin1Minecraft', 'Lassengg') AND game_duration > 800 AND game_mode = 'CLASSIC';"
    
    cursor.execute(query)
    players = cursor.fetchall()

    cursor.close()
    conn.close()
    return players
