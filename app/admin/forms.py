
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, SelectField, MultipleFileField, FileField
from wtforms.validators import DataRequired, Length, Optional


class PostForm(FlaskForm):
    
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
        'Görseller (Çoklu seçim)',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                       message='Sadece resim dosyaları yüklenebilir (jpg, png, gif, webp)')
        ]
    )
    submit = SubmitField('Paylaş')


class EditPostForm(PostForm):

    images = MultipleFileField(
        'Yeni Görseller Ekle (Opsiyonel)',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                       message='Sadece resim dosyaları yüklenebilir')
        ]
    )
    
    submit = SubmitField('Güncelle')


class ClubEditForm(FlaskForm):
    
    name = StringField(
        'Kulüp Adı',
        validators=[
            DataRequired(message='Kulüp adı gereklidir'),
            Length(min=3, max=200, message='Kulüp adı 3-200 karakter arasında olmalıdır')
        ]
    )
    
    about = TextAreaField(
        'Hakkında',
        validators=[Optional()]
    )
    
    achievements = TextAreaField(
        'Başarılarımız',
        validators=[Optional()]
    )
    
    location = StringField(
        'Konum',
        validators=[Optional(), Length(max=255)]
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
        validators=[Optional(), Length(max=120)]
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
    
    logo = FileField(
        'Logo',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                       message='Sadece resim dosyaları yüklenebilir')
        ]
    )
    
    submit = SubmitField('Kaydet')


class FeedbackForm(FlaskForm):
    
    club_id = SelectField(
        'Kulüp',
        coerce=int,  #Tarayıcıdan gelen veri string olarak gelir. gelen veriyi otomatik olarak integer çevirir
        validators=[
            DataRequired(message='Kulüp seçimi gereklidir')
        ]
    )
    
    title = StringField(
        'Başlık',
        validators=[
            DataRequired(message='Başlık gereklidir'),
            Length(min=5, max=255, message='Başlık 5-255 karakter arasında olmalıdır')
        ]
    )
    
    content = TextAreaField(
        'Geri Bildirim',
        validators=[
            DataRequired(message='Geri bildirim içeriği gereklidir'),
            Length(min=10, message='İçerik en az 10 karakter olmalıdır')
        ]
    )
    
    submit = SubmitField('Geri Bildirim Gönder')