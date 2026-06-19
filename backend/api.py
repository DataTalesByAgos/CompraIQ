import os
from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Habilitar CORS para conectar con el frontend en React

def get_db_connection():
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "supersecret")
    database = os.getenv("DB_NAME", "prices")
    
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

@app.route("/api/promotions", methods=["GET"])
def get_promotions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM promotions")
        promos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(promos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
