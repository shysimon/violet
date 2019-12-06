from flask import Blueprint

web = Blueprint("web", __name__)

from app.web import auth
from app.web import user
from app.web import app_song_sheet
from app.web import app_zone
from app.web import app_comment
from app.web import app_group_post
from app.web import app_thumbs
from app.web import app_user_recommend
from app.web import app_ads
from app.web import app_group_recommend
