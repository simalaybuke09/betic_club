"""
Flask Application Factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Extensions
db = SQLAlchemy() #veritabanı tablolarını Python classları olarak yönetmeyi sağlar .Veritabanındaki bir satır veri, Python'da bir nesne
login_manager = LoginManager() #session yönetir
migrate = Migrate()
csrf = CSRFProtect() #her form gönderildiğinde token kontrolü yapar


def create_app(config_name='default'):
    
    app = Flask(__name__)
    
    app.config.from_object('app.config.Config')
    

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
     
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bu sayfaya erişmek için lütfen giriş yapın.'
    login_manager.login_message_category = 'warning'
    
    # User loader
    #her sayfa yenilendiğinde kullanıcı id sorgulanır bu yüzden id ye göre kullanıcının veri tabanından bilgileri alınır ve nesnesi tutulur
    from app.models import Account
    
    @login_manager.user_loader
    def load_user(user_id):
        return Account.query.get(int(user_id))
    
    # Blueprints'leri kaydet ve bağlantıla
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.club import club_bp
    from app.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(club_bp, url_prefix='/club')
    app.register_blueprint(main_bp)  
    
    #veritabanından gelen ham tarih verisi filtrelenir
    #jinja2 html de {{datetime}} ile okunması sağlanır
    @app.template_filter('datetime')
    def format_datetime(value, format='%d.%m.%Y %H:%M'):
        """Tarih formatla"""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()  #hata olduğunda veritabanı işlemini geri çeker
        return render_template('errors/500.html'), 500
    
    # Upload klasörünü kontrol eder içeriğinde eğer yoksa oluşturur
    import os
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(os.path.join(upload_folder, 'club_logos'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'post_images'), exist_ok=True)
    
    return app