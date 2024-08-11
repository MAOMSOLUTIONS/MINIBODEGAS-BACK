from ..database import db
from datetime import datetime
from sqlalchemy.sql import func

from ..database import db

class AssetType(db.Model):
    id_asset_type = db.Column(db.Integer, primary_key=True)
    asset_type_name = db.Column(db.String(50), unique=True, nullable=False)
