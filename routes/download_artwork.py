from imports import *
from auth.config import ENVIRONMENT, AZURE_STORAGE_CONNECTION_STRING, AZURE_STORAGE_CONTAINER, UPLOAD_STORAGE
from azure.storage.blob import BlobServiceClient
from auth.azure_blob import connect_to_azure_blob
import tempfile
import sys

def download_artwork(app):
    @app.route('/download_artwork/<int:sale_id>', methods=['GET', 'POST'])
    @login_required
    def download_artwork_view(sale_id):
        try:
            sale = db.session.query(Sale).get(sale_id)
            if UPLOAD_STORAGE == 'local':
                file_path = os.path.join(app.root_path, "static", sale.filePath)
            
                print(f"ファイルパス: {sale.filePath}")
                
                f = open(file_path, 'rb') 
                print(f"ファイルダウンロード成功: {file_path}")
                return send_file(f, as_attachment=True, download_name=f"{sale.title}.png")
                    
            else:
                # Azure Blob Storage接続
                blob_service_client, container_client = connect_to_azure_blob(AZURE_STORAGE_CONTAINER)

                # URLからBlobの名前を適切に抽出
                if 'http' in sale.filePath:
                    # URLからファイル名を抽出 (例: https://example.blob.core.windows.net/container/image.png?...)
                    file_name = sale.filePath.split('/')[-1].split('?')[0]
                else:
                    # 相対パス
                    file_name = os.path.basename(sale.filePath)
                
                print(f'Blobファイル名: {file_name}')
                
                # ダウンロード処理
                blob_client = container_client.get_blob_client(file_name)
                blob_data = blob_client.download_blob().content_as_bytes()
                
                # 一時ファイルに保存
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(blob_data)
                    temp_file_path = temp_file.name
                
                print(f"一時ファイル作成完了: {temp_file_path}")
                return send_file(
                    temp_file_path, 
                    as_attachment=True, 
                    download_name=f"{sale.title}.png",
                    mimetype='image/png'
                )
        except Exception as e:
            print(f"ダウンロードエラー: {e}", file=sys.stderr)
            flash('ダウンロードに失敗しました', 'error')
            return redirect(url_for('myPage'))