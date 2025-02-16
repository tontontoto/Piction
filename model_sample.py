from imports import *

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_URL = os.environ.get("LOCAL_DB_URL")

Base = declarative_base()
engine = create_engine(DB_URL, echo=True)
db = SQLAlchemy()
	
saleCategoryAssociation = Table(
    'saleCategoryAssociation', db.metadata,
    Column('saleId', Integer, ForeignKey('sale.saleId'), primary_key=True),
    Column('categoryId', Integer, ForeignKey('category.categoryId'), primary_key=True)
)

# MARK: User
class User(UserMixin, db.Model):
    __tablename__ = "user"
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userName = db.Column(db.String(15))
    displayName = db.Column(db.String(10))
    mailAddress = db.Column(db.String(254))
    password = db.Column(db.String(254))
    registrationDate = db.Column(db.Date, default=date.today())
    iconFilePath = db.Column(db.String(254), nullable=False, default="img/icon_user_light.png")

    # usericon = db.relationship("UserIcon", back_populates="user", uselist=False)
    sales= db.relationship("Sale", back_populates="user")
    bids = db.relationship("Bid", back_populates="user") 
    likes = db.relationship("Like", back_populates="user")
    inquiries = db.relationship("Inquiry", back_populates="user")

    winning_buyer = db.relationship("WinningBid", foreign_keys="[WinningBid.buyerId]", back_populates="buyer")
    winning_seller = db.relationship("WinningBid", foreign_keys="[WinningBid.sellerId]", back_populates="seller")

    def get_id(self):
        return str(self.userId)

# # MARK:userIcon
# class UserIcon(db.Model):
#     __tablename__ = "userIcon"
#     iconId = db.Column(db.Integer, primary_key=True)
#     userId = db.Column(db.Integer, ForeignKey('user.userId'))  # UNIQUE 制約を削除
#     iconFilePath = db.Column(db.String(254), nullable=False)

#     user = db.relationship("User", back_populates="usericon")

# MARK:Category
class Category(db.Model):
    __tablename__ = "category"
    categoryId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoryName = db.Column(db.String(20))
    sales = db.relationship("Sale", secondary=saleCategoryAssociation, back_populates="categories", lazy='dynamic')

# MARK: Sale
class Sale(db.Model):
    __tablename__ = "sale"
    saleId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, ForeignKey('user.userId'))
    displayName = db.Column(db.String(10), ForeignKey('user.displayName'))
    title = db.Column(db.String(40), default="無題")
    displayName = db.Column(db.String(10))
    # categoryId = db.Column(db.Integer, ForeignKey('category.categoryId'))
    filePath = db.Column(db.String(254))
    startingPrice = db.Column(db.Integer)
    currentPrice = db.Column(db.Integer)
    creationTime = db.Column(db.String(5))
    startingTime = db.Column(db.String(19))
    finishTime = db.Column(db.String(19))
    saleStatus = db.Column(db.Boolean, default=True)

    user = db.relationship("User", back_populates="sales")
    categories = db.relationship("Category", secondary=saleCategoryAssociation, back_populates="sales", lazy='dynamic')
    bids = db.relationship("Bid", back_populates="sale")
    likes = db.relationship("Like", back_populates="sale")
    payment = db.relationship("Payment", back_populates="sale", uselist=False)

    @property
    def like_count(self):
        return Like.query.filter_by(saleId=self.saleId).count()

# MARK:Bid
class Bid(db.Model):    
    __tablename__ = "bid"
    bidId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    saleId = db.Column(db.Integer, ForeignKey('sale.saleId'))
    userId = db.Column(db.Integer, ForeignKey('user.userId'))

    bidPrice = db.Column(db.Integer)
    bidTime = db.Column(db.DATETIME, default=datetime.now, nullable=False)

    user = db.relationship("User", back_populates="bids")
    sale = db.relationship("Sale", back_populates="bids")
    winningBid = db.relationship("WinningBid", back_populates="bid", uselist=False)

# MARK:WinningBid
class WinningBid(db.Model):
    __tablename__ = "winningBid"
    winningBidId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyerId = db.Column(db.Integer, ForeignKey('user.userId'))
    saleId = db.Column(db.Integer, ForeignKey('sale.saleId'))
    sellerId = db.Column(db.Integer, ForeignKey('user.userId'))
    bidId = db.Column(db.Integer, ForeignKey('bid.bidId'))

    buyer = db.relationship("User", foreign_keys=[buyerId], back_populates="winning_buyer") 
    seller = db.relationship("User", foreign_keys=[sellerId], back_populates="winning_seller") 
    bid = db.relationship("Bid", back_populates="winningBid")
    payment = db.relationship("Payment", backref="winningBid", uselist=False)
    
# MARK:PaymentWay
class PaymentWay(db.Model):
    __tablename__ = "paymentWay"
    paymentWayId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paymentWayName = db.Column(db.String(20))
    payments = db.relationship("Payment", back_populates="paymentWay")

# Payment
class Payment(db.Model):
    __tablename__ = "payment"
    paymentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    saleId = db.Column(db.Integer, ForeignKey('sale.saleId'))
    winningBidId = db.Column(db.Integer, ForeignKey('winningBid.winningBidId'))
    paymentWayId = db.Column(db.Integer, ForeignKey('paymentWay.paymentWayId'))
    paymentDate = db.Column(db.DATETIME, default=datetime.now(), nullable=False)

    sale = db.relationship("Sale", back_populates="payment")
    paymentWay = db.relationship("PaymentWay", back_populates="payments")
    amount = db.Column(db.Integer)

# MARK: Like
class Like(db.Model):
    __tablename__ = "like"
    likeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, ForeignKey('user.userId'))
    saleId = db.Column(db.Integer, ForeignKey('sale.saleId'))

    user = db.relationship("User", back_populates="likes")
    sale = db.relationship("Sale", back_populates="likes")

# MARK: InquiryKind
class InquiryKind(db.Model):
    __tablename__ = "inquiryKind"
    inquiryKindId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inquiryKindName = db.Column(db.String(10))

    inquiries = db.relationship("Inquiry", back_populates="inquiryKind")

# MARK: Inquiry
class Inquiry(db.Model):
    __tablename__ = "inquiry"
    inquiryId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, ForeignKey('user.userId'))
    displayName = db.Column(db.String(10))
    mailAddress = db.Column(db.String(254))
    inquiryKindId = db.Column(db.Integer, ForeignKey('inquiryKind.inquiryKindId'))
    appendFile = db.Column(db.String(30))
    inquiryContent = db.Column(db.String(500))
    inquiryAnswer = db.Column(db.String(500))

    user = db.relationship("User", back_populates="inquiries")
    inquiryKind = db.relationship("InquiryKind", foreign_keys=[inquiryKindId], back_populates="inquiries")

