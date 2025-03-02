# 重複しているインポートをまとめた部分
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user, login_manager
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta, date
from sqlalchemy import Column, ForeignKey, Table, String, Integer, Date, DATETIME, func, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from functools import wraps
import logging, logging.config
import os
bcrypt = Bcrypt()

# 個別に異なるインポート
from model_sample import db, User, Sale, Category, Bid, Like, Inquiry, WinningBid, PaymentWay, Payment, saleCategoryAssociation
from sqlalchemy.ext.declarative import declarative_base
from azure.storage.blob import BlobServiceClient
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from logging import getLogger
import random
import string
import base64
import pymysql

# # ログの設定
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__) 