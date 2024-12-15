# Abonnement-Service

Abonnement-Service is a Flask-based microservice that handles subscription management. It includes endpoints for creating subscriptions, retrieving subscription details, updating subscription statuses, and generating subscription reports. The service uses SQLite for database management and provides API documentation via Swagger.

## Features
	•	Create Subscriptions: Add new subscriptions with customer details and terms.
	•	Retrieve Subscriptions: Fetch subscription details by their unique ID.
	•	Update Subscription Status: Change the status of a subscription (e.g., Active, Inactive, Terminated).
	•	Subscription Reporting: Generate reports summarizing active, inactive, and terminated subscriptions.
	•	API Documentation: Integrated Swagger UI for exploring and testing endpoints.

## Requirements

### Python Packages
	•	Python 3.7 or higher
	•	Flask
	•	Flasgger
	•	Python-Dotenv
	•	SQLite (built into Python)

### Python Dependencies

Install the required dependencies using:
```Pip install -r requirements.txt```

### Environment Variables

Create a .env file in the root directory and specify the following:
```FLASK_DEBUG=1```
```DATABASE=abonnement-database.db```

## Getting Started

1. Initialize the Database

The service uses SQLite to store invoice data. The database is automatically initialized when the service starts. To reinitialize, you can modify the init_db() function in abonnement-app.py.

2. Start the Service

Run the Flask application:
```python abonnement-app.py```
The service will be available at http://127.0.0.1:5002.

## API Endpoints

1. GET /

Provides a list of available endpoints in the service.

#### Response Example:
```
{
  "service": "Abonnement-Service",
  "available_endpoints": [
    {"path": "/create_subscription", "method": "POST", "description": "Create a new subscription"},
    {"path": "/get_subscription/<int:abonnement_id>", "method": "GET", "description": "Retrieve subscription by ID"},
    {"path": "/update_status/<int:abonnement_id>", "method": "PUT", "description": "Update subscription status"},
    {"path": "/report", "method": "GET", "description": "Generate subscription report"}
  ]
}
```

2. POST /create_subscription

Creates a new subscription.

#### Request Body:
```
{
  "kunde_id": 123,
  "start_dato": "2024-01-01",
  "slut_dato": "2024-12-31",
  "månedlig_pris": 499.99,
  "kilometer_graense": 1500,
  "kontrakt_periode": "12 months"
}
```

#### Response Example:
```
{
  "message": "Subscription created",
  "subscription_id": 1
}
```

3. GET /get_subscription/<int:abonnement_id>

Retrieves the details of a subscription by its unique ID.

#### Response Example:
```
{
  "abonnement_id": 1,
  "kunde_id": 123,
  "start_dato": "2024-01-01",
  "slut_dato": "2024-12-31",
  "månedlig_pris": 499.99,
  "kilometer_graense": 1500,
  "kontrakt_periode": "12 months",
  "status": "Active"
}
```

4. PUT /update_status/<int:abonnement_id>

Updates the status of a subscription.

#### Request Body:
```
{
  "status": "Terminated"
}
```

#### Response Example:
```
{
  "message": "Status updated"
}
```

5. GET /report

Generates a summary report of all subscriptions.

#### Response Example:
```
{
  "ActiveSubscriptions": 10,
  "InactiveSubscriptions": 5,
  "TerminatedSubscriptions": 2
}
```
## Project Structure
```
.
├── abonnement-app.py       # Main Flask application
├── abonnement-database.db  # SQLite database (created automatically)
├── swagger/                # YAML files for API documentation
│   ├── create_subscription.yaml
│   ├── get_subscription.yaml
│   ├── update_status.yaml
│   ├── report.yaml
│   └── home.yaml
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md               # Project documentation
```

## Development Notes

### Swagger Documentation
	•	Swagger is available at /apidocs.
	•	API specifications are written in YAML and stored in the swagger/ folder.

### Database Management
####	•	Initialization: Automatically initializes the database on start.
####	•	Schema:
	•	abonnement_id: Unique subscription ID (primary key).
	•	kunde_id: Customer ID (foreign key from the customer database).
	•	start_dato: Start date of the subscription.
	•	slut_dato: End date of the subscription.
	•	månedlig_pris: Monthly price.
	•	kilometer_graense: Monthly mileage limit.
	•	kontrakt_periode: Contract period (e.g., “12 months”).
	•	status: Subscription status (Active, Inactive, Terminated).

## Contributions

Feel free to fork the repository and submit pull requests. For major changes, open an issue to discuss what you would like to change.

## License

This project is licensed under the MIT License. See LICENSE for more information.