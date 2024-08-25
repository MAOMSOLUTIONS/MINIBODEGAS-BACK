from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db

class AssetType(db.Model):
    id_asset_type = db.Column(Integer, primary_key=True)
    asset_type_name = db.Column(String(50), unique=True, nullable=False)
