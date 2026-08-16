# Zipco ETL Pipeline

An Apache Airflow batch ETL pipeline that cleans and normalizes Zipco food transaction data, then publishes the resulting datasets to Azure Blob Storage.

## Pipeline overview

The Airflow DAG runs the following tasks in order:

1. **Extract** — reads `dataset/raw_data/zipco_transaction.csv` into a pandas DataFrame.
2. **Transform** — removes duplicates, fills missing values, and creates normalized product, customer, staff, and transaction datasets.
3. **Load** — uploads the raw data and normalized datasets to Azure Blob Storage.

The DAG is named `zipco_food_dag` and is scheduled to run every 10 minutes.

## Project structure

```text
.
├── dags/
│   └── dag_script.py          # Airflow DAG definition
├── dataset/
│   ├── raw_data/              # Source transaction data
│   └── cleaned_data/          # Generated normalized CSV files
├── notebooks/
│   └── Etl_pipeline.ipynb     # Exploratory notebook
├── scripts/
│   ├── extraction.py          # Extract stage
│   ├── transformation.py      # Transform stage
│   └── loading.py             # Azure Blob Storage load stage
├── .env.example               # Environment variable template
└── requirements.txt           # Python dependencies
```

## Prerequisites

- Python 3
- An Azure Storage account and Blob container (required for the load stage)

## Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/esodevops/zipco-airflow-etl-pipeline.git
cd zipco-airflow-etl-pipeline
```

Replace `<your-github-username>` with the GitHub account or organization that owns the repository.

Create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
AZURE_STORAGE_CONNECTION_STRING=your-azure-storage-connection-string
CONTAINER_NAME=your-container-name
```

Keep `.env` private. It is excluded from version control.

## Run the pipeline locally

Run only the transformation stage to generate the normalized CSV files under `dataset/cleaned_data/`:

```bash
python -m scripts.transformation
```

Run the complete pipeline, including the upload to Azure Blob Storage:

```bash
python -m scripts.loading
```

The load stage writes these blobs:

```text
raw/cleaned_zipco_transaction_data.csv
processed/products.csv
processed/customers.csv
processed/staff.csv
processed/transactions.csv
```

## Run with Apache Airflow

Set Airflow's local home and DAG directory from the project root, initialize the metadata database, and start Airflow:

```bash
export AIRFLOW_HOME="$PWD/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$PWD/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_USERS="admin:admin"

airflow db migrate
airflow standalone
```

Open the URL printed by Airflow (normally `http://localhost:8080`), sign in with the generated credentials, enable `zipco_food_dag`, and trigger it manually or allow its schedule to run.

To display the generated local password:

```bash
cat "$AIRFLOW_HOME/simple_auth_manager_passwords.json.generated"
```

## Configure Airflow SMTP alerts

The DAG sends an email when a run fails. It uses the Airflow connection ID `smtp_default` and reads the sender and recipient address from `AIRFLOW_ALERT_EMAIL`.

The SMTP provider is included in `requirements.txt`. After installing the project dependencies, export your alert address before starting Airflow:

```bash
export AIRFLOW_ALERT_EMAIL="your-email@example.com"
```

### Gmail example

For Gmail, enable two-step verification and create an app password. Use the app password rather than your normal account password. Then create the Airflow SMTP connection:

```bash
read -s -p "Gmail app password: " SMTP_APP_PASSWORD
echo
export SMTP_APP_PASSWORD

airflow connections delete smtp_default 2>/dev/null || true
airflow connections add smtp_default \
  --conn-type smtp \
  --conn-host smtp.gmail.com \
  --conn-port 587 \
  --conn-login "$AIRFLOW_ALERT_EMAIL" \
  --conn-password "$SMTP_APP_PASSWORD" \
  --conn-extra '{"disable_ssl": true, "from_email": "your-email@example.com"}'

unset SMTP_APP_PASSWORD
```

Replace the `from_email` value with the same address assigned to `AIRFLOW_ALERT_EMAIL`. Port `587` uses STARTTLS, so SSL is disabled while TLS remains enabled.

For another mail provider, replace the host, port, username, and TLS/SSL options with the values supplied by that provider. Common configurations are:

- Port `587`: STARTTLS with `disable_ssl` set to `true`.
- Port `465`: implicit SSL; omit `disable_ssl`.

Verify that Airflow can see the connection:

```bash
airflow connections get smtp_default
```

Restart `airflow standalone` after exporting `AIRFLOW_ALERT_EMAIL`. To test the notification, trigger a controlled DAG failure and confirm that the alert arrives. Do not commit SMTP passwords or app passwords to `.env`, the DAG, or the README.

## Generated outputs

The transformation stage creates:

- `clean_data.csv` — cleaned source records
- `products.csv` — unique products and prices
- `customers.csv` — unique customer details
- `staff.csv` — unique staff details
- `transactions.csv` — transaction facts linked to normalized IDs

These files, along with Airflow runtime state, logs, local databases, credentials, and Python virtual environments, are intentionally ignored by Git.

## Security notes

- Never commit `.env`, Azure connection strings, or generated Airflow passwords.
- Use a least-privilege Azure credential that can access only the required container.
- Rotate any credential immediately if it is exposed in source control or logs.
