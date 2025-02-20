from imports import *
from auth.config import ENVIRONMENT, AZURE_STORAGE_CONTAINER, ALLOWED_EXTENSIONS
from auth.azure_blob import connect_to_azure_blob

# Azure Blob Storage接続
blob_service_client, container_client = connect_to_azure_blob()

# ファイルの拡張子を確認するヘルパー関数
def allowed_file(filename):
    # ファイル名に拡張子が含まれているかを確認
    if '.' in filename:
        # ファイル名を拡張子で分割して、拡張子が許可されたものかを確認
        file_extension = filename.rsplit('.', 1)[1].lower()
        return file_extension in ALLOWED_EXTENSIONS
    return False

# MARK: canvas→画像変換
def decode_image(image_data):
    try:
        image_data = image_data.split(",")[1]
        return base64.b64decode(image_data)
    except (IndexError, base64.binascii.Error):
        return None

# MARK: 画像保存
if ENVIRONMENT == 'local':
    # ローカルフォルダに保存
    def save_image_to_file(image_bytes, upload_folder):
        try:
            file_name = f"image_{len(os.listdir(upload_folder)) + 1}.png"
            file_path = os.path.join(upload_folder, file_name).replace('\\', '/')
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            return file_path
        except Exception as e:
            print(f"Error 画像保存失敗: {e}")
            return None
else:
    # Azure Blob Storageに保存
    def save_image_to_azure(image_bytes):
        try:
            # ランダムなファイル名を生成
            file_name = f"image_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}.png"

            # Azure Blob Storageに画像をアップロード
            blob_client = container_client.get_blob_client(file_name)
            blob_client.upload_blob(image_bytes, overwrite=True)

            # アップロードされた画像のURLを取得
            blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER}/{file_name}"
            return blob_url
        except Exception as e:
            print(f"Error 画像保存失敗: {e}")
            return None