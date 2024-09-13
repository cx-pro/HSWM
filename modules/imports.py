from collections import UserDict

from importlib.resources import path

from gevent.pywsgi import WSGIServer
from flask_compress import Compress

import fcntl

# import rsa

from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import send_from_directory
from flask import flash
from flask import abort
from flask import jsonify
from flask import make_response

from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import join_room
from flask_socketio import leave_room

from geventwebsocket.handler import WebSocketHandler

import os
import sys

import re

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageFilter

import random as rd

import json
import orjson

import requests

import datetime
import pytz

import smtplib, ssl

from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import AnonymousUserMixin
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import fresh_login_required
from flask_login import current_user

import time

from copy import deepcopy

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

from linebot import LineBotApi
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent
from linebot.models import PostbackEvent
from linebot.models import TextMessage
from linebot.models import TextSendMessage
from linebot.models import FlexSendMessage

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from google.auth.transport import requests as grequests
import pathlib
import string
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from google.oauth2 import service_account

import uuid

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from collections import OrderedDict

import logging

import calendar

import pyexcel_ods3

import qrcode

import imghdr

import sqlite3


import firebase_admin
from firebase_admin import messaging
    

from apscheduler.schedulers.background import BackgroundScheduler

calen = calendar.Calendar()


pdfmetrics.registerFont(TTFont('kaiu', "static/pdf/kaiu.ttf"))
pdfmetrics.registerFont(TTFont('kaiub', "static/pdf/kaiub.TTC"))
registerFontFamily("kaiu", normal="kaiu", bold="kaiub")

channel_access_token=os.environ.get('Channel_access_token',os.environ.get("CHANNEL_ACCESS_TOKEN"))
channel_secret=os.environ.get('Channel_secret',os.environ.get("CHANNEL_SECRET"))
if channel_access_token and channel_secret:
  line_bot_api = LineBotApi(channel_access_token)
  handler = WebhookHandler(channel_secret)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

imgs_files = [
  "svg", "ico", "jpg", "jfif", "jpeg", "png", "webp", "bmp", "avif"
]

google_auth_needs = dict()

lp=[""]

def setScheduler():
  return BackgroundScheduler(timezone='Asia/Taipei')
