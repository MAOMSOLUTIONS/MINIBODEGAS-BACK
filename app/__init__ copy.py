# app/__init__.py
from flask import Flask
from app.api import api_blueprint
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from .database import db  
from flask_migrate import Migrate
from flask_mail import Mail


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tu_clave_secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # Inicializar db con la aplicación Flask
    migrate = Migrate(app, db)

    app.config['MAIL_SERVER'] = 'smtp.office365.com'  # Reemplaza con la dirección de tu servidor SMTP
    app.config['MAIL_PORT'] = 587  # Reemplaza con el puerto correcto
    app.config['MAIL_USERNAME'] = 'miguel.ochoa@cinlatlogistics.com'  # Reemplaza con tu dirección de correo
    app.config['MAIL_PASSWORD'] = 'Otro'  # Reemplaza con tu contraseña de correo
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    mail = Mail(app)  # Configura Flask-Mail aquí

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    return app, mail

# Crear la instancia de la aplicación Flask y la instancia de Mail
#app = Flask(__name__)
#app.config['SECRET_KEY'] = 'tu_clave_secreta'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db.init_app(app)  # Inicializar db con la aplicación Flask
#mail = Mail(app)  # Configura Flask-Mail aquí

#migrate = Migrate(app, db)

#CORS(app, resources={r"/api/*": {"origins": "*"}})
#app.register_blueprint(api_blueprint, url_prefix='/api')
