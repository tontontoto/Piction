from imports import *
from auth.config import UPLOAD_STORAGE
from auth.azure_blob import connect_to_azure_blob
from auth.img_helper import *
import pytz
import sys
import base64

def add_sale(app):
    
    @app.route('/get_category_name', methods=['POST'])
    def get_category_name():
        try:
            # フロントエンドから送られてきたcategoryIdを取得
            data = request.get_json()
            category_id = data.get('categoryId')

            # categoryIdを使ってカテゴリ名を取得
            category = Category.query.filter_by(categoryId=category_id).first()

            if category:
                # カテゴリが見つかった場合、カテゴリ名を返す
                return jsonify({'categoryName': category.categoryName})
            else:
                # カテゴリが見つからない場合
                return jsonify({'error': 'Category not found'}), 404

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'Failed to fetch category name'}), 500
        
    # MARK:　出品ページ
    @app.route('/add_sale', methods=['POST'])
    @login_required
    def add_sale_view():
        try:
            data = request.get_json()
            title = data.get('title')
            posting_date = data.get('postingDate')  # 例: "3月4日 (火)"
            posting_time_range = data.get('postingTime')  # 例: "9時～10時"
            image_data = data.get('image')
            time = data.get('time')
            price = data.get('price')
            kategori = data.get('kategori')

            print(f"出品情報: {title}, {posting_date}, {posting_time_range}, {kategori}")

            # カテゴリ情報を取得
            category = Category.query.filter_by(categoryId=kategori).first()
            if not category:
                return jsonify({'error': 'Category not found'}), 400

            print(f"選択されたカテゴリ名: {category.categoryName}")

        except Exception as e:
            print(f"Error 出品情報取得失敗: {e}")
            return jsonify({'error': 'Failed to parse request data'}), 400

        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        # Base64デコード
        if image_data.startswith("data:image/png;base64,"):
            image_data = image_data.replace("data:image/png;base64,", "")

        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            print(f"Error: Base64 decoding failed - {e}")
            return jsonify({'error': 'Invalid image data'}), 400

        # 現在の日本時間を取得
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        current_minutes = now.minute  # 現在の「分」を取得

        # 日付と時間範囲から掲載開始時刻を計算
        try:
            # 今日の年を取得し、"3月4日 (火)" をパース
            current_year = now.year
            posting_date = posting_date.split(" (")[0]  # "3月4日" にする
            posting_datetime = datetime.strptime(f"{current_year}年{posting_date}", "%Y年%m月%d日")

            # 時間範囲 "9時～10時" から開始時刻を取得
            start_hour = int(posting_time_range.split("時～")[0])  # "9" を取得
            posting_datetime = posting_datetime.replace(hour=start_hour, minute=0, second=0)

            # 日本時間に変換
            posting_datetime = pytz.timezone('Asia/Tokyo').localize(posting_datetime)

            print("掲載開始時刻:", posting_datetime.strftime('%Y/%m/%d %H:%M:%S'))
        except Exception as e:
            print(f"Error 掲載開始時間の計算失敗: {e}")
            return jsonify({'error': 'Failed to calculate posting time'}), 400

        # 掲載終了時刻の計算（現在の「分」を適用）
        posting_end_datetime = posting_datetime.replace(minute=current_minutes)

        print("掲載終了時刻:", posting_end_datetime.strftime('%Y/%m/%d %H:%M:%S'))

        # 画像保存
        if UPLOAD_STORAGE == 'local':
            file_path = save_image_to_file(image_bytes, app.config['UPLOAD_FOLDER'])
            file_path = file_path.replace(app.config['UPLOAD_FOLDER'], 'upload_images')
        else:
            try:
                file_path = save_image_to_azure(image_bytes)
                if not file_path:
                    return jsonify({"error": "Failed to save image"}), 500
            except Exception as e:
                return jsonify({"message": "Image uploaded successfully", "image_url": file_path}), 201

        # ユーザー情報取得
        userId = session.get('userId')
        try:
            user = db.session.query(User).get(userId)
        except Exception as e:
            print(f"Error ユーザー情報取得失敗: {e}")
            return jsonify({'error': 'Failed to query user'}), 500

        displayName = user.displayName

        try:
            # 出品データをデータベースに追加
            new_sale = Sale(
                userId=userId,
                displayName=displayName,
                title=title,
                filePath=file_path,
                startingPrice=price,
                currentPrice=price,
                creationTime=time,
                startingTime=posting_datetime.strftime('%Y/%m/%d %H:%M:%S'),
                finishTime=posting_end_datetime.strftime('%Y/%m/%d %H:%M:%S')
            )
            db.session.add(new_sale)
            db.session.commit()
        except Exception as e:
            print(f"Error 出品処理失敗: {e}")
            return jsonify({'error': 'Failed to create sale'}), 500

        try:
            # 中間テーブルにカテゴリ関連を追加
            new_association = saleCategoryAssociation.insert().values(saleId=new_sale.saleId, categoryId=kategori)
            db.session.execute(new_association)
            db.session.commit()
        except Exception as e:
            print(f"Error 中間テーブルへの追加失敗: {e}")
            return jsonify({'error': 'Failed to associate sale with category'}), 500

        return jsonify({'message': 'Sale added successfully'}), 201