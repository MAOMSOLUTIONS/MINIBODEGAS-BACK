from ..database import db
from datetime import datetime
from sqlalchemy.sql import func

from ..database import db

class AssetStatus(db.Model):
    id_status = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50), unique=True, nullable=False)