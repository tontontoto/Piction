from sqlalchemy import Column, ForeignKey, Table, String, Integer, Date, DATETIME, text, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
Base = declarative_base()
engine = create_engine('sqlite:///example.db')
db = SQLAlchemy()
	
saleCategoryAssociation = Table(
    'saleCategoryAssociation', db.metadata,
    Column('saleId', String(6), ForeignKey('sale.saleId')),
    Column('categoryId', String(5), ForeignKey('category.categoryId'))
)

class User(UserMixin, db.Model):
    __tablename__ = "user"
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userName = db.Column(db.String(15))
    displayName = db.Column(db.String(10))
    mailAddress = db.Column(db.String(254))
    password = db.Column(db.String(15))
    registrationDate = db.Column(db.Date, default=date.today())

    sales= db.relationship("Sale", back_populates="user")
    bids = db.relationship("Bid", back_populates="user") 
    likes = db.relationship("Like", back_populates="user")
    inquiries = db.relationship("Inquiry", back_populates="user")

    winning_buyer = db.relationship("WinningBid", foreign_keys="[WinningBid.buyerId]", back_populates="buyer")
    winning_seller = db.relationship("WinningBid", foreign_keys="[WinningBid.sellerId]", back_populates="seller")

    def get_id(self):
        return str(self.userId)


class Category(db.Model):
    __tablename__ = "category"
    categoryId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoryName = db.Column(db.String(20))
    sales = db.relationship("Sale", secondary=saleCategoryAssociation, back_populates="categories")


class Sale(db.Model):
    __tablename__ = "sale"
    saleId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, ForeignKey('user.userId'))
    displayName = db.Column(db.String(10), ForeignKey('user.displayName'))
    title = db.Column(db.String(40), default="無題")
    displayName = db.Column(db.String(10))
    categoryId = db.Column(db.Integer, ForeignKey('category.categoryId'))
    filePath = db.Column(db.String(30))
    startingPrice = db.Column(db.Integer)
    currentPrice = db.Column(db.Integer)
    creationTime = db.Column(db.String(5))
    startingTime = db.Column(db.DATETIME, default=datetime.now, nullable=False)
    finishTime = db.Column(db.DATETIME, default=datetime.now, nullable=False)
    saleStatus = db.Column(db.Boolean, default=True)

    user = db.relationship("User", back_populates="sales")
    categories = db.relationship("Category", secondary=saleCategoryAssociation, back_populates="sales")
    bids = db.relationship("Bid", back_populates="sale")
    likes = db.relationship("Like", back_populates="sale")
    payment = db.relationship("Payment", back_populates="sale", uselist=False)

    @property
    def like_count(self):
        return Like.query.filter_by(saleId=self.saleId).count()

# 入札テーブル
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


class WinningBid(db.Model):
    __tablename__ = "winningBid"
    winningBidId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyerId = db.Column(db.Integer, ForeignKey('user.userId'))
    sellerId = db.Column(db.Integer, ForeignKey('user.userId'))
    bidId = db.Column(db.Integer, ForeignKey('bid.bidId'))

    buyer = db.relationship("User", foreign_keys=[buyerId], back_populates="winning_buyer") 
    seller = db.relationship("User", foreign_keys=[sellerId], back_populates="winning_seller") 
    bid = db.relationship("Bid", back_populates="winningBid")
    payment = db.relationship("Payment", backref="winningBid", uselist=False)
    

class PaymentWay(db.Model):
    __tablename__ = "paymentWay"
    paymentWayId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paymentWayName = db.Column(db.String(20))
    payments = db.relationship("Payment", back_populates="paymentWay")


class Payment(db.Model):
    __tablename__ = "payment"
    paymentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    saleId = db.Column(db.String(6), ForeignKey('sale.saleId'))
    winningBidId = db.Column(db.Integer, ForeignKey('winningBid.winningBidId'))
    paymentWayId = db.Column(db.Integer, ForeignKey('paymentWay.paymentWayId'))
    paymentDate = db.Column(db.DATETIME, default=datetime.now(), nullable=False)

    sale = db.relationship("Sale", back_populates="payment")
    paymentWay = db.relationship("PaymentWay", back_populates="payments")
    amount = db.Column(db.Integer)


class Like(db.Model):
    __tablename__ = "like"
    likeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, ForeignKey('user.userId'))
    saleId = db.Column(db.Integer, ForeignKey('sale.saleId'))

    user = db.relationship("User", back_populates="likes")
    sale = db.relationship("Sale", back_populates="likes")

class InquiryKind(db.Model):
    __tablename__ = "inquiryKind"
    inquiryKindId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inquiryKindName = db.Column(db.String(10))

    inquiries = db.relationship("Inquiry", back_populates="inquiryKind")

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

