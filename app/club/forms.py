"""
Club Forms
Kulüp profil ve paylaşım formları
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, FileField, MultipleFileField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Email


class PostForm(FlaskForm):
    """
    Kulüp paylaşım formu
    """
    title = StringField(
        'Başlık',
        validators=[
            DataRequired(message='Başlık gereklidir'),
            Length(min=5, max=255, message='Başlık 5-255 karakter arasında olmalıdır')
        ]
    )
    
    content = TextAreaField(
        'İçerik',
        validators=[
            DataRequired(message='İçerik gereklidir'),
            Length(min=10, message='İçerik en az 10 karakter olmalıdır')
        ]
    )
    
    images = MultipleFileField(
        'Görseller (Çoklu seçim yapabilirsiniz)',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                       message='Sadece resim dosyaları yüklenebilir (jpg, png, gif, webp)')
        ]
    )
    
    submit = SubmitField('Paylaş')


class EditPostForm(PostForm):
    """
    Paylaşım düzenleme formu. PostForm'dan miras alır.
    """
    # title ve content alanları PostForm'dan miras alınır.
    
    images = MultipleFileField(
        'Yeni Görseller Ekle (Opsiyonel)',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                       message='Sadece resim dosyaları yüklenebilir')
        ]
    )
    submit = SubmitField('Güncelle')



class ClubProfileForm(FlaskForm):
    """
    Kulüp profil düzenleme formu
    """
    name = StringField(
        'Kulüp Adı',
        validators=[
            DataRequired(message='Kulüp adı gereklidir'),
            Length(min=3, max=200, message='Kulüp adı 3-200 karakter arasında olmalıdır')
        ]
    )
    
    logo = FileField(
        'Logo',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                       message='Sadece resim dosyaları yüklenebilir')
        ]
    )
    
    about = TextAreaField(
        'Hakkımızda',
        validators=[
            DataRequired(message='Hakkımızda bölümü gereklidir'),
            Length(min=20, message='En az 20 karakter girmelisiniz')
        ]
    )
    
    achievements = TextAreaField(
        'Başarılarımız',
        validators=[Optional()]
    )
    
    location = StringField(
        'Konum',
        validators=[
            DataRequired(message='Konum gereklidir'),
            Length(max=255)
        ]
    )
    
    member_count = StringField(
        'Üye Sayısı',
        validators=[Optional()]
    )
    
    
    phone = StringField(
        'Telefon',
        validators=[Optional(), Length(max=20)]
    )
    
    email_contact = StringField(
        'İletişim E-posta',
        validators=[Optional(), Email(message='Geçerli bir e-posta adresi giriniz'), Length(max=120)]
    )
    
  
    instagram = StringField(
        'Instagram',
        validators=[Optional(), Length(max=100)]
    )
    
    twitter = StringField(
        'Twitter',
        validators=[Optional(), Length(max=100)]
    )
    
    linkedin = StringField(
        'LinkedIn',
        validators=[Optional(), Length(max=100)]
    )
    
    facebook = StringField(
        'Facebook',
        validators=[Optional(), Length(max=100)]
    )
    
    website = StringField(
        'Website',
        validators=[Optional(), Length(max=200)]
    )
    
    submit = SubmitField('Profili Güncelle')


class MessageForm(FlaskForm):
    """Yeni mesaj gönderme formu"""
    recipient_id = SelectField(
        'Alıcı Kulüp',
        coerce=int,
        validators=[DataRequired(message='Alıcı seçimi gereklidir')]
    )
    content = TextAreaField(
        'Mesajınız',
        validators=[
            DataRequired(message='Mesaj içeriği boş olamaz.'),
            Length(min=1, max=5000)
        ],
        render_kw={'rows': 5, 'placeholder': 'Mesajınızı buraya yazın...'}
    )
    submit = SubmitField('Gönder')
