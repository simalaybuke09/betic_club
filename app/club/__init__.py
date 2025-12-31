"""
Club Blueprint
Kulüp paneli ve işlemleri
"""
from flask import Blueprint

club_bp = Blueprint('club', __name__)

from app.club import routes