from imports import *

def download_artwork(app):
    @app.route('/download_artwork/<int:sale_id>', methods=['GET', 'POST'])
    @login_required
    def download_artwork_view(sale_id):
        sale = Sale.query.get(sale_id)
        file_path = os.path.join(app.root_path, "static", sale.filePath) 
        
        print(f"ファイルパス: {sale.filePath}")

        try:
            f = open(file_path, 'rb') 
            print(f"ファイルダウンロード成功: {file_path}")
            return send_file(f, as_attachment=True, download_name=f"{sale.title}.png")
            
        except Exception as e:
            print(f"Error: {e}")
            print('ダウンロードに失敗しました', 'error')
            return redirect(url_for('myPage'))