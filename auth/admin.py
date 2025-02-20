from imports import *

# MARK: 管理者画面
class LikeModelView(ModelView):
    # 一覧表示のカラム設定
    column_list = ['likeId', 'user.displayName', 'sale.title']
    
    # 外部キーの表示名を設定
    column_labels = {
        'likeId': 'いいねID',
        'user.displayName': 'ユーザー名',
        'sale.title': '作品タイトル'
    }
    
    # リレーションの表示設定
    column_formatters = {
        'user.displayName': lambda v, c, m, p: m.user.displayName if m.user else '',
        'sale.title': lambda v, c, m, p: m.sale.title if m.sale else ''
    }

class BidModelView(ModelView):
    column_list = ['bidId', 'user.displayName', 'sale.title', 'bidPrice', 'bidTime']
    
    column_labels = {
        'bidId': '入札ID',
        'user.displayName': '入札者',
        'sale.title': '作品タイトル',
        'bidPrice': '入札価格',
        'bidTime': '入札時間'
    }
    
    column_formatters = {
        'user.displayName': lambda v, c, m, p: m.user.displayName if m.user else '',
        'sale.title': lambda v, c, m, p: m.sale.title if m.sale else ''
    }

# 管理画面の設定
def init_admin(app):
    admin = Admin(app, name='Piction', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session, name='ユーザー'))
    admin.add_view(ModelView(Sale, db.session, name='出品'))
    admin.add_view(ModelView(Category, db.session, name='カテゴリー'))
    admin.add_view(BidModelView(Bid, db.session, name='入札履歴'))
    admin.add_view(LikeModelView(Like, db.session, name='いいね'))
    admin.add_view(ModelView(Inquiry, db.session, name='お問い合わせ'))