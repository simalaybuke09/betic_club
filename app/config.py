"""
Flask Configuration
"""
import os
from dotenv import load_dotenv

# .env dosyasındaki verileri python içine enjekte 
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))


class Config:
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    #.env de varsa oradan alır yoksa hata vermemesi için geçici bir geliştirme anahtarı atar

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False #nesne üzerindeki her küçük değişikliği takip edip sinyaller göndermesi
    SQLALCHEMY_ECHO = False  # SQL sorgularını göster 
    
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(basedir), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max dosya boyutu
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Pagination
    POSTS_PER_PAGE = 10
    CLUBS_PER_PAGE = 12
    
    # Security
    WTF_CSRF_ENABLED = True #token
    WTF_CSRF_TIME_LIMIT = None  # CSRF token süresi (None = süresiz)
    SESSION_COOKIE_SECURE = False  # Production'da True yap çünkü localde HTTPS sertifikası yok
    SESSION_COOKIE_HTTPONLY = True #cookie dosyasına sadece HTTP/HTTPS üzerinden erişilebilir. JS ile erişilemez
    SESSION_COOKIE_SAMESITE = 'Lax' #Başka bir siteden uygulamaya girileceğinde GET isteklerini kabul eder cookie gönderir POST kabul etmez
    
    # Admin hesabı (ilk kurulumda oluşturmak için)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@uni.edu.tr'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    
    # Hava durumu API ayarları
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY') or None
    WEATHER_CITY = os.environ.get('WEATHER_CITY') or 'Trabzon'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    # Production'da SECRET_KEY mutlaka .env den gelmeli
    @property
    def SECRET_KEY(self):
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            raise ValueError("SECRET_KEY environment variable is not set!")
        return secret_key


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/club_platform_test'
    WTF_CSRF_ENABLED = False



config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}