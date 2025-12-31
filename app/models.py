"""
Database Models
"""
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from slugify import slugify


class Account(UserMixin, db.Model):
    
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(20), nullable=False) 
    is_approved = db.Column(db.Boolean, default=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    club = db.relationship('Club', backref='account', uselist=False, #One-to-One
                          cascade='all, delete-orphan', lazy=True) #veri sadece çağrıldığında db den çekilir
    posts = db.relationship('Post', backref='author', lazy='dynamic', #veriden önce sorgu döndürür
                           cascade='all, delete-orphan') #Ebeveyn ölürse, çocuklar da ölür
    #One-to-Many
    
    # Mesajlaşma ilişkileri
    messages_sent = db.relationship('Message', 
                                   foreign_keys='Message.sender_id',
                                   backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message', 
                                       foreign_keys='Message.recipient_id',
                                       backref='recipient', lazy='dynamic')
    
    def __repr__(self):
        return f'<Account {self.username}>' #nesnelerin okunabilir hali,terminalde görmek için
    
    def set_password(self, password):
        """Şifreyi hashle ve kaydet"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Şifreyi doğrula"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Admin mi kontrol et"""
        return self.account_type == 'admin'
    
    def is_club(self):
        """Kulüp mü kontrol et"""
        return self.account_type == 'club'
    
    def can_post(self):
        """Paylaşım yapabilir mi?"""
        if self.is_admin():
            return True
        if self.is_club() and self.is_approved:
            return True
        return False


class Club(db.Model):
   
    __tablename__ = 'clubs'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    logo = db.Column(db.String(255))
    
    
    about = db.Column(db.Text)  
    achievements = db.Column(db.Text)  
    location = db.Column(db.String(255))  
    member_count = db.Column(db.Integer, default=0) 
    
    
    phone = db.Column(db.String(20))
    email_contact = db.Column(db.String(120))
    instagram = db.Column(db.String(100))
    twitter = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    facebook = db.Column(db.String(100))
    website = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    feedbacks = db.relationship('Feedback', backref='club', lazy='dynamic', 
                               cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Club {self.name}>'
    
    def generate_slug(self):
        """URL-friendly slug oluştur"""
        base_slug = slugify(self.name) #Türkçe karakterleri İngilizce karşılıklarına çevirir, boşlukları - yapar ve tüm harfleri küçültür.
        slug = base_slug
        counter = 1
        
        # Eğer slug varsa sonuna sayı ekle URL çakışması yaşanmaması için
        while Club.query.filter_by(slug=slug).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        self.slug = slug
    
    def get_posts(self):
        """Kulübün paylaşımlarını getir"""
        return Post.query.filter_by(account_id=self.account_id)\
            .order_by(Post.created_at.desc()).all()
    
    def get_post_count(self):
        """Toplam paylaşım sayısı"""
        return Post.query.filter_by(account_id=self.account_id).count()
    
    def has_social_media(self):
        """Sosyal medya hesabı var mı?"""
        return any([self.instagram, self.twitter, self.linkedin, 
                   self.facebook, self.website])


class Post(db.Model):

    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255)) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    def get_author_name(self):
        """Paylaşımı yapan kulüp veya admin adını döndür"""
        if self.author.is_admin():
            return "Üniversite Yönetimi"
        elif self.author.is_club() and self.author.club:
            return self.author.club.name
        return "Bilinmeyen"
    
    def get_author_logo(self):
        """Paylaşımı yapan kulüp logosunu döndür"""
        if self.author.is_club() and self.author.club and self.author.club.logo:
            return self.author.club.logo
        return None
    
    def get_club(self):
        """Eğer kulüp paylaşımıysa kulüp nesnesini döndür"""
        if self.author.is_club():
            return self.author.club
        return None
    
    def get_author_slug(self):
        """Paylaşımı yapan kulübün slug'ını döndür (profil linklemek için)"""
        if self.author.is_club() and self.author.club:
            return self.author.club.slug
        return None
    
    def is_by_admin(self):
        """Admin paylaşımı mı?"""
        return self.author.is_admin()
    
    def can_edit(self, user):
        """Kullanıcı bu paylaşımı düzenleyebilir mi?"""
        if user.is_admin():
            return True
        if user.id == self.account_id:
            return True
        return False
    
    def get_images(self):
        """Paylaşım resimlerini liste olarak döndür"""
        if not self.image:
            return []
        return [img.strip() for img in self.image.split(',') if img.strip()]
            #boşlukları temizler                            #boşsa listeye eklemez
    def get_excerpt(self, length=200):
        """İçeriğin kısa özeti"""
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + '...'


class Message(db.Model):

    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.recipient_id}>'


class Feedback(db.Model):
   
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Gönderen hesaba erişim
    sender = db.relationship('Account', foreign_keys=[sender_id])