"""
Auth Forms
Giriş ve kayıt formları
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import Account, Club
from wtforms.validators import Optional


class LoginForm(FlaskForm):
    """
    Giriş formu (Kulüp ve Admin için)
    """
    username = StringField(
        'Kulüp Adı',
        validators=[
            DataRequired(message='Kulüp adı gereklidir')
        ]
    )
    
    password = PasswordField(
        'Şifre',
        validators=[
            DataRequired(message='Şifre gereklidir')
        ]
    )
    
    submit = SubmitField('Giriş Yap')


class RegisterForm(FlaskForm):
    """
    Kulüp kayıt formu
    """
    username = StringField(
        'Kulüp Adı',
        validators=[
            DataRequired(message='Kulüp adı gereklidir'),
            Length(min=3, max=200, message='Kulüp adı 3-200 karakter arasında olmalıdır')
        ]
    )
    
    email = StringField(
        'E-posta',
        validators=[
            DataRequired(message='E-posta gereklidir'),
            Email(message='Geçerli bir e-posta adresi giriniz')
        ]
    )
    
    about = TextAreaField(
        'Kulüp Hakkında',
        validators=[
            DataRequired(message='Kulüp hakkında bilgisi gereklidir'),
            Length(min=20, message='En az 20 karakter girmelisiniz')
        ]
    )
    
    location = StringField(
        'Kulüp Yeri',
        validators=[
            DataRequired(message='Kulüp yeri gereklidir'),
            Length(max=255)
        ]
    )

    achievements = TextAreaField(
        'Başarılarımız (Opsiyonel)',
        validators=[Optional()]
    )

    member_count = StringField(
        'Üye Sayısı (Opsiyonel)',
        validators=[Optional()]
    )
    
    phone = StringField(
        'Telefon (Opsiyonel)',
        validators=[Optional(), Length(max=20)]
    )
    
 
    instagram = StringField(
        'Instagram Kullanıcı Adı (Opsiyonel)',
        validators=[Optional(), Length(max=100)]
    )
    
    twitter = StringField(
        'Twitter Kullanıcı Adı (Opsiyonel)',
        validators=[Optional(), Length(max=100)]
    )
    
    logo = FileField(
        'Logo',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                       message='Sadece resim dosyaları yüklenebilir (jpg, png, gif, webp)')
        ]
    )
    
    password = PasswordField(
        'Şifre',
        validators=[
            DataRequired(message='Şifre gereklidir'),
            Length(min=6, message='Şifre en az 6 karakter olmalıdır')
        ]
    )
    
    confirm_password = PasswordField(
        'Şifre Tekrar',
        validators=[
            DataRequired(message='Şifre tekrarı gereklidir'),
            EqualTo('password', message='Şifreler eşleşmiyor')
        ]
    )
    
    submit = SubmitField('Kayıt Ol')
    
    def validate_username(self, username):
        """Kulüp adı benzersiz mi kontrol et"""
        account = Account.query.filter_by(username=username.data).first()
        if account:
            raise ValidationError('Bu kulüp adı zaten kullanılıyor. Lütfen farklı bir isim seçin.')
    
    def validate_email(self, email):
        """E-posta benzersiz mi kontrol et"""
        account = Account.query.filter_by(email=email.data).first()
        if account:
            raise ValidationError('Bu e-posta adresi zaten kayıtlı. Lütfen farklı bir e-posta kullanın.')