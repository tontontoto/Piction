from imports import *
from auth.config import ENVIRONMENT, DB_URL, UPLOAD_STORAGE, AZURE_STORAGE_CONNECTION_STRING, AZURE_STORAGE_CONTAINER
from azure.storage.blob import BlobServiceClient

def connect_to_azure_blob(container_name):
    if UPLOAD_STORAGE == 'blob' and AZURE_STORAGE_CONNECTION_STRING:
        try:
            blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(container_name)
            print("Azure Blob Storage connected successfully")
            return blob_service_client, container_client
        except Exception as e:
            print(f"Azure Blob Storage connection failed: {e}")
            print(f"DEBUG: container_client = {container_client}")
            return None, None
    return None, None