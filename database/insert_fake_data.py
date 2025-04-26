from model_sample import db, User, Sale, Category, PaymentWay

# ---- ユーザーデータの仮挿入 ----
def add_users():
    dummy_users = [
        User(userName='artist1', displayName='山田太郎', mailAddress='yamada@example.com', password='111111'),
        User(userName='artist2', displayName='鈴木花子', mailAddress='suzuki@example.com', password='222222'),
        User(userName='artist3', displayName='佐藤一郎', mailAddress='sato@example.com', password='333333'),
        User(userName='artist4', displayName='田中美咲', mailAddress='tanaka@example.com', password='444444'),
        User(userName='artist5', displayName='高橋健一', mailAddress='takahashi@example.com', password='555555')
    ]
    
    db.session.add_all(dummy_users)
    db.session.commit()

# ---- カテゴリデータの仮挿入 ----
def add_categories():
    dummy_categories = [
        Category(categoryName='キャラクター'),
        Category(categoryName='模写'),
        Category(categoryName='空想'),
        Category(categoryName='抽象'),
        Category(categoryName='カラフル'),
        Category(categoryName='風景'),
        Category(categoryName='動物'),
        Category(categoryName='静物'),
        Category(categoryName='ポートレート'),
    ]
    
    try:
        db.session.add_all(dummy_categories)
        db.session.commit()
    except Exception as e:
        print(f"Error カテゴリ追加処理失敗: {e}")
        db.session.rollback()
        dummy_categories = []
        
    return dummy_categories

# ---- 商品データの仮挿入 ----
def add_sales(dummy_categories):    
    dummy_sales = [
        Sale(
            userId=1, 
            displayName='山田太郎', 
            title='一眼レフ', 
            filePath='upload_images/camera.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='10:00',
            startingTime='2024/03/20 10:00:00',
            finishTime='2025/04/20 10:00:00'
        ),
        Sale(
            userId=2, 
            displayName='鈴木花子', 
            title='パソコン', 
            filePath='upload_images/pc.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='11:30',
            startingTime='2024/03/20 11:30:00',
            finishTime='2025/04/20 11:30:00'
        ),
        Sale(
            userId=3, 
            displayName='佐藤一郎', 
            title='ゾウ', 
            filePath='upload_images/elephant.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='12:45',
            startingTime='2024/03/20 12:45:00',
            finishTime='2025/04/20 12:45:00'
        ),
        Sale(
            userId=4, 
            displayName='田中美咲', 
            title='お魚', 
            filePath='upload_images/fish2.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='14:15',
            startingTime='2024/03/20 14:15:00',
            finishTime='2025/04/20 14:15:00'
        ),
        Sale(
            userId=5, 
            displayName='高橋健一', 
            title='雪だるま', 
            filePath='upload_images/snowman.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='15:30',
            startingTime='2024/03/20 15:30:00',
            finishTime='2025/04/20 15:30:00'
        ),
        Sale(
            userId=5, 
            displayName='高橋健一', 
            title='いちご', 
            filePath='upload_images/strawberry.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='15:30',
            startingTime='2024/03/20 15:30:00',
            finishTime='2025/04/20 15:30:00'
        ),
        Sale(
            userId=5, 
            displayName='高橋健一', 
            title='タピオカ', 
            filePath='upload_images/tapioca.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='15:30',
            startingTime='2024/03/20 15:30:00',
            finishTime='2025/04/20 15:30:00'
        ),
        Sale(
            userId=1, 
            displayName='山田太郎', 
            title='ヨット', 
            filePath='upload_images/yacht.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='15:30',
            startingTime='2024/03/20 15:30:00',
            finishTime='2025/04/20 15:30:00'
        ),
    ]

    # カテゴリーの割り当て
    dummy_sales[0].categories.extend([dummy_categories[5], dummy_categories[2]])  # 風景、空想
    dummy_sales[1].categories.extend([dummy_categories[4], dummy_categories[7]])  # カラフル、静物
    dummy_sales[2].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル
    dummy_sales[3].categories.extend([dummy_categories[5], dummy_categories[2]])  # 風景、空想
    dummy_sales[4].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル
    dummy_sales[5].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル
    dummy_sales[6].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル
    dummy_sales[7].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル

    db.session.add_all(dummy_sales)
    db.session.commit()