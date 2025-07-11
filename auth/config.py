# config.py 設定情報（環境変数など）

from imports import *

# 環境設定の取得
# ENVIRONMENT = os.getenv('ENVIRONMENT')
ENVIRONMENT = 'local'
if not ENVIRONMENT:
    raise ValueError("app.py 環境変数 ENVIRONMENT が設定されていません")

if ENVIRONMENT == 'local':
    # 環境変数の読み込み
    load_dotenv()

# 環境設定の取得
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

# データベースURLの設定
DB_URL = os.getenv('DB_URL')

# Azure Blob Storage設定
AZURE_STORAGE_ACCOUNT = os.getenv('AZURE_STORAGE_ACCOUNT')
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER')
AZURE_STORAGE_SAS = os.getenv('AZURE_STORAGE_SAS')

AZURE_STORAGE_ICON_CONTAINER = os.getenv('AZURE_STORAGE_ICON_CONTAINER')
AZURE_STORAGE_ICON_SAS = os.getenv('AZURE_STORAGE_ICON_SAS')

# アプリケーション設定
UPLOAD_STORAGE = os.getenv('UPLOAD_STORAGE', 'blob')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './static/upload_images')
UPLOAD_ICON_FOLDER = './static/upload_icon'

# 許可する拡張子
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 管理者画面のURL
ADMIN_URL = os.getenv('ADMIN_URL', '/admin')
