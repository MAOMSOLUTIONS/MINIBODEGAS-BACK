from ..database import db
from datetime import datetime
from sqlalchemy.sql import func

class Enterprise(db.Model):
    id_enterprise = db.Column(db.Integer, primary_key=True)
    enterprise_name = db.Column(db.String(80), unique=True, nullable=False)
    rfc = db.Column(db.String(50))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))
