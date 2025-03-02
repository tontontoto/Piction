from imports import *
from flask_admin.form import rules
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
import locale
from datetime import datetime

# 基本ModelViewクラス - 共通機能を実装
class BaseModelView(ModelView):
    def __init__(self, model, session, **kwargs):
        super(BaseModelView, self).__init__(model, session, **kwargs)
    
    # フォーム生成の挙動をオーバーライド
    def scaffold_form(self):
        form_class = super(BaseModelView, self).scaffold_form()
        
        # ここでフォームのフィールドを調整できます
        return form_class
    
    # このメソッドを実装することで、フォームの事前処理ができます
    def on_form_prefill(self, form, id):
        pass

    # リスト表示の設定
    page_size = 15
    can_view_details = True
    
    # 編集可能項目の制御
    can_edit = True
    can_create = True
    can_delete = True
    
    # 安全なアクセスヘルパー
    @staticmethod
    def safe_attr(obj, attr_name, default=None):
        try:
            if '.' in attr_name:
                parts = attr_name.split('.')
                value = obj
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    else:
                        return default
                return value
            else:
                return getattr(obj, attr_name, default)
        except:
            return default
            
    # 価格フォーマット
    @staticmethod
    def format_price(price):
        if price is None:
            return "¥0"
        try:
            return f"¥{int(price):,}"
        except:
            return str(price)

# ModelView クラスを基底クラスから派生させる
class UserModelView(BaseModelView):
    column_list = ['userId', 'displayName', 'mailAddress']
    column_labels = {
        'displayName': '表示名',
        'mailAddress': 'メールアドレス',
    }
    column_searchable_list = ['displayName', 'mailAddress']

class SaleModelView(BaseModelView):
    column_list = ['saleId', 'title', 'currentPrice', 'saleStatus']
    column_labels = {
        'saleId': '出品ID',
        'title': 'タイトル',
        'currentPrice': '現在価格',
        'saleStatus': '状態'
    }
    column_formatters = {
        'currentPrice': lambda v, c, m, p: BaseModelView.format_price(getattr(m, 'currentPrice', None))
    }
    column_searchable_list = ['title']

class CategoryModelView(BaseModelView):
    column_list = ['categoryId', 'categoryName']
    column_labels = {
        'categoryId': 'カテゴリID',
        'categoryName': 'カテゴリ名'
    }

class BidModelView(BaseModelView):
    column_list = ['bidId', 'saleId', 'bidPrice']
    column_labels = {
        'bidId': '入札ID',
        'saleId': '商品ID',
        'bidPrice': '入札価格'
    }
    column_formatters = {
        'bidPrice': lambda v, c, m, p: BaseModelView.format_price(getattr(m, 'bidPrice', None))
    }

class LikeModelView(BaseModelView):
    column_list = ['likeId', 'saleId', 'userId']
    column_labels = {
        'likeId': 'いいねID',
        'saleId': '商品ID',
        'userId': 'ユーザーID'
    }

class WinningBidModelView(BaseModelView):
    column_list = ['winningBidId', 'saleId', 'buyerId', 'sellerId']
    column_labels = {
        'winningBidId': '落札ID',
        'saleId': '商品ID',
        'buyerId': '買主ID',
        'sellerId': '出品者ID'
    }

class InquiryModelView(BaseModelView):
    column_list = ['inquiryId', 'userId', 'displayName', 'mailAddress']
    column_labels = {
        'inquiryId': '問合せID',
        'userId': 'ユーザーID',
        'displayName': '表示名', 
        'mailAddress': 'メールアドレス'
    }

# 管理画面の設定
def init_admin(app):
    admin = Admin(app, name='Piction 管理パネル', template_mode='bootstrap3')
    
    # エラー抑制設定
    app.config['FLASK_ADMIN_RAISE_ON_VIEW_EXCEPTION'] = False
    
    # 各モデルの登録
    try:
        admin.add_view(UserModelView(User, db.session, name='ユーザー管理'))
        admin.add_view(SaleModelView(Sale, db.session, name='出品管理'))
        admin.add_view(CategoryModelView(Category, db.session, name='カテゴリー管理'))
        admin.add_view(BidModelView(Bid, db.session, name='入札履歴'))
        admin.add_view(LikeModelView(Like, db.session, name='いいね管理'))
        admin.add_view(WinningBidModelView(WinningBid, db.session, name='落札管理'))
        admin.add_view(InquiryModelView(Inquiry, db.session, name='お問い合わせ管理'))
    except Exception as e:
        print(f"管理画面設定エラー: {e}")