# config.py 設定情報（環境変数など）

from imports import *

# 環境変数の読み込み
load_dotenv()

# 環境設定の取得
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

# データベースURLの設定
if ENVIRONMENT == 'local':
    DB_URL = os.getenv('LOCAL_DB_URL')
else:
    DB_URL = os.getenv('AZURE_DB_URL')

# Azure Blob Storage設定
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER')
AZURE_STORAGE_SAS = os.getenv('AZURE_STORAGE_SAS')



# アプリケーション設定
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './static/upload_images')
UPLOAD_ICON_FOLDER = './static/upload_icon'

# 許可する拡張子
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
