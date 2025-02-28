from imports import *
from auth.img_helper import allowed_file
from sqlalchemy.sql import select
from azure.storage.blob import BlobServiceClient, ContentSettings
from auth.azure_blob import connect_to_azure_blob
from auth.config import AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_CONNECTION_STRING, AZURE_STORAGE_CONTAINER, AZURE_STORAGE_ICON_SAS, AZURE_STORAGE_ICON_CONTAINER

# MARK: マイページ
def mypage(app):
    @app.route('/myPage', methods=['GET', 'POST'])
    @login_required
    def myPage_view():
        userId = session.get('userId')
        try:
            user = db.session.query(User).get(userId)
            # session(ログイン状態のuserId)のsaleの行を取り出し、
            # 外部キーのuserIdよりUserテーブルの中のデータを参照できる。
            sales = db.session.query(Sale).join(User).filter_by(userId=userId).all()
        except Exception as e:
            print(f"Error マイページの情報取得失敗: {e}")
            user = None
            sales = []
            
        for sale in sales:
            display_name = sale.user.displayName
            title = sale.title
            print(title)
            print(f"ユーザーの表示名: {display_name}")
        
        # ユーザーの出品数の取得
        try:
            listingCount = db.session.query(Sale).filter(Sale.userId == userId).count()
        except Exception as e:
            print(f"Error 出品数のカウントに失敗: {e}")
            listingCount = "---"

        # いいねした数の取得
        try:
            likeCount = db.session.query(Like).filter(Like.userId == userId).count()
        except Exception as e:
            print(f"Error いいねした商品のカウントに失敗: {e}")
            likeCount = "---"
        
        # 自分が落札した商品の情報を取得
        myBidList = db.session.query(WinningBid).join(Sale).filter(WinningBid.buyerId == userId).all()

        # 落札した商品の情報を取得
        myBidSales = []
        for bid in myBidList:
            sale = Sale.query.get(bid.saleId)
            myBidSales.append(sale)

        print("落札した商品の一覧", myBidSales)
        
        # 自分が入札した作品を取得
        # 最新のBidを取得するためのサブクエリ
        latest_bid_subquery = (
            db.session.query(
                func.max(Bid.bidId).label("latest_bid_id")
            )
            .join(Sale, Bid.saleId == Sale.saleId)
            .filter(Bid.userId == userId)
            .group_by(Sale.saleId)
            .subquery()
        )

        # 最新のBidを持つSale情報を取得
        my_bids_query = (
            db.session.query(Bid, Sale, User)
            .join(Sale, Bid.saleId == Sale.saleId)
            .join(User, Sale.userId == User.userId)
            .filter(Bid.bidId.in_(select(latest_bid_subquery)))
            .order_by(Bid.bidId.desc())  # 最新のBid順に並べる
            .all()
        )
        
        my_bids = []
        for bid in my_bids_query:
            sale = Sale.query.get(bid.Sale.saleId)
            my_bids.append(sale)
            
        
        # 売上情報の取得
        saleStatus = db.session.query(Sale).filter(Sale.userId == userId, Sale.saleStatus == 0).all()
        sale_ids = [sale.saleId for sale in saleStatus]  
        revenue = db.session.query(func.sum(Payment.amount)).filter(Payment.saleId.in_(sale_ids)).scalar() or 0
        
        # POSTメソッドでフォームが送信されたとき
        if request.method == 'POST':
            displayName = request.form.get('displayName')
            userName = request.form.get('userName')
            mailAddress = request.form.get('mailAddress')

            # 'file'がフォームから送信されているか確認
            if 'file' not in request.files:
                return 'ファイルが送信されていません'

            file = request.files['file']
            iconFilePath = user.iconFilePath  # 既存のアイコンパスを保持

            # 新しいアイコンが送信されている場合
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_extension = filename.rsplit('.', 1)[1].lower()

                    # ユーザーごとの固有ファイル名を決定
                    if iconFilePath == "static/img/icon_user_light.png":
                        print('アイコン 新規保存')
                        new_filename = f"user_icon_{user.userId}.{file_extension}"
                    else:
                        print('アイコン 更新保存')
                        # 既にアイコンアップロード済みの場合、既存のファイル名を利用（Azureの場合はSAS等のクエリ文字列を除外）
                        new_filename = os.path.basename(iconFilePath.split('?')[0])
                        base, ext = os.path.splitext(new_filename)
                        if ext.lower() != f".{file_extension}":
                            new_filename = f"user_icon_{user.userId}.{file_extension}"
                    
                    if app.config['IS_LOCAL']:
                        print('アイコン ローカル保存')
                        # ディレクトリが存在しない場合、作成する
                        os.makedirs(app.config['UPLOAD_ICON_FOLDER'], exist_ok=True)
                        file_path = os.path.join(app.config['UPLOAD_ICON_FOLDER'], new_filename).replace('\\', '/')

                        # 既存のアイコンがあれば削除（オプション）
                        if iconFilePath and os.path.exists(os.path.join(app.config['UPLOAD_ICON_FOLDER'], iconFilePath.split('/')[-1])):
                            try:
                                os.remove(os.path.join(app.config['UPLOAD_ICON_FOLDER'], iconFilePath.split('/')[-1]))
                                print(f"既存のアイコンファイル({iconFilePath})を削除しました。")
                            except Exception as e:
                                print(f"既存のアイコン削除に失敗しました: {e}")

                        # 新しい画像ファイルを保存
                        try:
                            file.save(file_path)
                            print(f"新しいアイコンが保存されました: {file_path}")
                            iconFilePath = f"upload_icon/{new_filename}"  # 新しいアイコンファイルパス
                        except Exception as e:
                            print(f"ファイルの保存に失敗しました: {e}")
                            iconFilePath = None
                    else:
                        print('アイコン Azure Blob Storage保存')
                         # Azure Blob Storageにアップロードする場合
                        try:
                            # Azure Blob Storage接続
                            blob_service_client, container_client = connect_to_azure_blob(AZURE_STORAGE_ICON_CONTAINER)
                            content_settings = ContentSettings(content_type=file.content_type)
                            # ファイルポインタを先頭に戻す
                            file.seek(0)
                            container_client.upload_blob(new_filename, file, overwrite=True, content_settings=content_settings)
                            # BlobのURLをiconFilePathに設定
                            iconFilePath = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{AZURE_STORAGE_ICON_CONTAINER}/{new_filename}?{AZURE_STORAGE_ICON_SAS}"
                            print(f"新しいアイコンがBlob Storageに保存されました: {iconFilePath}")
                        except Exception as e:
                            print(f"Blob Storageへのアップロードに失敗しました: {e}")
                            iconFilePath = None

            # ユーザー情報をデータベースに保存
            try:
                if user:
                    # アイコンの更新があった場合のみ新しいアイコンパスを保存
                    if iconFilePath:
                        user.iconFilePath = iconFilePath

                    # 表示名やユーザー名、メールアドレスも更新する場合があれば
                    user.displayName = displayName
                    user.userName = userName
                    user.mailAddress = mailAddress

                    for sale in sales:
                        sale.displayName = displayName
                    
                    db.session.commit()
                    print('ユーザー情報が保存されました！')
                else:
                    print('ユーザーが見つかりませんでした。')
            except Exception as e:
                db.session.rollback()
                print(f"データベース保存エラー: {e}")

            # リダイレクトでフォーム送信後の再送信を防ぐ
            return render_template('myPage.html', user=user, sales=sales, listingCount=listingCount, likeCount=likeCount, myBidSales=myBidSales, my_bids=my_bids, revenue=revenue, config=app.config)
            

        return render_template('myPage.html', user=user, sales=sales, listingCount=listingCount, likeCount=likeCount, myBidSales=myBidSales, my_bids=my_bids, revenue=revenue, config=app.config)
