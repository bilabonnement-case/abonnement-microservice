from flask import Flask, jsonify, request
import os
from datetime import datetime
from dotenv import load_dotenv
from flasgger import Swagger, swag_from
import sqlite3

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Swagger Configuration
app.config['SWAGGER'] = {
    'title': 'Abonnement Microservice API',
    'uiversion': 3,
    'openapi': '3.0.0'
}
swagger = Swagger(app)

# Database Opsætning
DATABASE = "/app/data/abonnement-database.db"


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Drop tabellen, hvis den allerede eksisterer
        ##cursor.execute("DROP TABLE IF EXISTS subscriptions")
        # Opret en tabel til fakturaer, hvis den ikke allerede findes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            abonnement_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique subscription ID
            kunde_id INTEGER NOT NULL,                      -- Foreign key for customer
            bil_id INTEGER NOT NULL,                        -- Foreign key for car
            start_dato DATE NOT NULL,                       -- Subscription start date
            slut_dato DATE NOT NULL,                        -- Subscription end date
            månedlig_pris REAL NOT NULL,                    -- Monthly price
            kilometer_graense INTEGER NOT NULL,             -- Monthly mileage limit
            kontrakt_periode TEXT NOT NULL,                 -- Contract period (e.g., "6 months")
            status TEXT NOT NULL                            -- Subscription status
        )
        """)
        conn.commit()


init_db()

# Enum for Subscription Status
class SubscriptionStatus:
    ACTIVE = "Aktiv"
    INACTIVE = "Inaktiv"
    TERMINATED = "Opsagt"


@app.route('/')
@swag_from('swagger/home.yaml')
def home():
    return jsonify({
        "service": "Abonnement-Service",
        "available_endpoints": [
            {"path": "/create_subscription", "method": "POST", "description": "Create a new subscription"},
            {"path": "/get_subscription/<int:abonnement_id>", "method": "GET", "description": "Get subscription by ID"},
            {"path": "/update_status/<int:abonnement_id>", "method": "PUT", "description": "Update subscription status"},
            {"path": "/report", "method": "GET", "description": "Generate subscription report"}
        ]
    })


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/create_subscription', methods=['POST'])
@swag_from('swagger/create_subscription.yaml')
def create_subscription():
    try:
        data = request.get_json()

        kunde_id = data.get("kunde_id")
        bil_id = data.get("bil_id")  # Ny parameter
        start_dato = data.get("start_dato")
        slut_dato = data.get("slut_dato")
        månedlig_pris = data.get("månedlig_pris")
        kilometer_graense = data.get("kilometer_graense")
        kontrakt_periode = data.get("kontrakt_periode")
        status = SubscriptionStatus.ACTIVE

        # Validate required fields
        if not all([kunde_id, bil_id, start_dato, slut_dato, månedlig_pris, kilometer_graense, kontrakt_periode]):
            return jsonify({"error": "Missing required fields"}), 400

        # Insert into database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO subscriptions (kunde_id, bil_id, start_dato, slut_dato, månedlig_pris, kilometer_graense, kontrakt_periode, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (kunde_id, bil_id, start_dato, slut_dato, månedlig_pris, kilometer_graense, kontrakt_periode, status))
            conn.commit()

            abonnement_id = cursor.lastrowid

        return jsonify({"message": "Subscription created", "subscription_id": abonnement_id}), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500


@app.route('/get_subscription/<int:abonnement_id>', methods=['GET'])
@swag_from('swagger/get_subscription.yaml')
def get_subscription(abonnement_id):
    with get_db_connection() as conn:
        subscription = conn.execute("SELECT * FROM subscriptions WHERE abonnement_id = ?", (abonnement_id,)).fetchone()

    if subscription is None:
        return jsonify({"error": "Subscription not found"}), 404

    return jsonify(dict(subscription)), 200


@app.route('/update_status/<int:abonnement_id>', methods=['PUT'])
@swag_from('swagger/update_status.yaml')
def update_status(abonnement_id):
    try:
        data = request.get_json()
        status = data.get("status")

        if status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.INACTIVE, SubscriptionStatus.TERMINATED]:
            return jsonify({"error": "Invalid status"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
            UPDATE subscriptions
            SET status = ?
            WHERE abonnement_id = ?
            """, (status, abonnement_id))
            conn.commit()

            if result.rowcount == 0:
                return jsonify({"error": "Subscription not found"}), 404

        return jsonify({"message": "Status updated"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500


@app.route('/report', methods=['GET'])
@swag_from('swagger/report.yaml')
def report():
    with get_db_connection() as conn:
        active_count = conn.execute("SELECT COUNT(*) FROM subscriptions WHERE status = ?", (SubscriptionStatus.ACTIVE,)).fetchone()[0]
        inactive_count = conn.execute("SELECT COUNT(*) FROM subscriptions WHERE status = ?", (SubscriptionStatus.INACTIVE,)).fetchone()[0]
        terminated_count = conn.execute("SELECT COUNT(*) FROM subscriptions WHERE status = ?", (SubscriptionStatus.TERMINATED,)).fetchone()[0]

    report_data = {
        "ActiveSubscriptions": active_count,
        "InactiveSubscriptions": inactive_count,
        "TerminatedSubscriptions": terminated_count
    }

    return jsonify(report_data)

@app.route('/delete_subscription/<int:abonnement_id>', methods=['DELETE'])
@swag_from('swagger/delete_subscription.yaml')
def delete_subscription(abonnement_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = cursor.execute("DELETE FROM subscriptions WHERE abonnement_id = ?", (abonnement_id,))
            conn.commit()

            if result.rowcount == 0:
                return jsonify({"error": "Subscription not found"}), 404

        return jsonify({"message": f"Subscription with ID {abonnement_id} deleted"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500



if __name__ == '__main__':
    app.run(debug=bool(int(os.getenv('FLASK_DEBUG', 0))), host='0.0.0.0', port=5001)