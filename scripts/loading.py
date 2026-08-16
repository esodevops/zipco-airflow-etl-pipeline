import os
import pandas as pd
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from scripts.extraction import extraction
from scripts.transformation import read_clean_data

# Load environment variables from .env file
load_dotenv()

def loading():
    data = extraction()
    products, customers, staff, transactions = read_clean_data()

    # Create a BlobServiceClient object
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('CONTAINER_NAME')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(container_name)

    # Load data to Azure Blob Storage
    # List of tuples (DataFrame, Blob Name)
    files = [
        (data, "raw/cleaned_zipco_transaction_data.csv"),
        (products, "processed/products.csv"),
        (customers, "processed/customers.csv"),
        (staff, "processed/staff.csv"),
        (transactions, "processed/transactions.csv")
    ]

    # Load data to Azure Blob Storage
    for file, blob_name in files:
        blob_client = container_client.get_blob_client(blob_name)
        output = file.to_csv(index=False)
        blob_client.upload_blob(output, overwrite=True)
        print(f"{blob_name} loaded into Azure Blob Storage.")

if __name__ == "__main__":
    loading()
