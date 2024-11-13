from flask import Flask, jsonify
from flask_cors import CORS
import pymysql

# Configuração do Flask
app = Flask(__name__)
CORS(app)  

# Configurações do banco de dados
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "LolData"
}

# Função para conectar ao banco de dados MariaDB
def connect_db():
    return pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# Rota para obter os dados da tabela match_info
@app.route('/matches', methods=['GET'])
def get_matches():
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM match_info")
            result = cursor.fetchall()
            return jsonify(result)
    finally:
        connection.close()

# Rota para obter os dados da tabela participants
@app.route('/participants', methods=['GET'])
def get_participants():
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM participants")
            result = cursor.fetchall()
            return jsonify(result)
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
