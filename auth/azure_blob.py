from imports import *
from auth.config import ENVIRONMENT, DB_URL, UPLOAD_FOLDER

def connect_to_azure_blob():
    if os.getenv('ENVIRONMENT') == 'azure' and os.getenv('AZURE_STORAGE_CONNECTION_STRING'):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
            container_client = blob_service_client.get_container_client(os.getenv('AZURE_STORAGE_CONTAINER'))
            print("Azure Blob Storage connected successfully")
            return blob_service_client, container_client
        except Exception as e:
            print(f"Azure Blob Storage connection failed: {e}")
            return None, None
    return None, None