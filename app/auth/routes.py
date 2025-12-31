"""
Auth Routes
Kimlik doğrulama route'ları
"""
import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm
from app.models import Account, Club
from app import db
from werkzeug.utils import secure_filename
import uuid


def save_image(file, folder):
    """Resim kaydetme yardımcı fonksiyonu"""
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex[:10]}_{filename}" 
        #Dosya isminin başına rastgele 10 karakterli benzersiz bir kod ekle
        
        #Klasör yollarını bilgisayarın işletim sistemine uygun şekilde birleştirir.
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        #Dosyayı RAM'den alıp fiziksel olarak diske yazar.
        
        return f"{folder}/{unique_filename}"
    return None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    
    # Zaten giriş yapmışsa yönlendir
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_club():
            if current_user.is_approved:
                return redirect(url_for('club.dashboard'))
            else:
                flash('Hesabınız henüz onaylanmadı. Lütfen yönetimin onayını bekleyin.', 'warning')
                return redirect(url_for('main.home'))
    
    form = LoginForm()
    
    if form.validate_on_submit():  #Form POST isteğiyse
        # Kulüp adı ile kullanıcıyı bul
        account = Account.query.filter_by(username=form.username.data).first()
        
        # Kullanıcı var mı ve şifre doğru mu?
        if account is None or not account.check_password(form.password.data):
            flash('Kulüp adı veya şifre hatalı.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Kulüp ise onaylı mı kontrol et
        if account.is_club() and not account.is_approved:
            flash('Hesabınız henüz onaylanmadı. Lütfen yönetimin onayını bekleyin.', 'warning')
            return redirect(url_for('main.home'))
        
        # Giriş yap
        login_user(account, remember=True)
        
        # URL den nereye gitmek istediğine bakar ona göre yönlendirir
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        # Hesap tipine göre yönlendir
        if account.is_admin():
            flash('Admin paneline hoş geldiniz!', 'success')
            return redirect(url_for('admin.dashboard'))
        elif account.is_club():
            flash(f'Hoş geldiniz, {account.club.name}!', 'success')
            return redirect(url_for('club.dashboard'))
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Kulüp kayıt sayfası
    """
    # Zaten giriş yapmışsa yönlendir
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_club():
            return redirect(url_for('club.dashboard'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Hesap oluştur (username = kulüp adı)
        account = Account(
            username=form.username.data,  
            email=form.email.data,
            account_type='club',
            is_approved=False  
        )
        account.set_password(form.password.data)
        
        db.session.add(account)
        db.session.flush()  # ID'yi al
        
        # Logo kaydet
        logo_path = None
        if form.logo.data:
            logo_path = save_image(form.logo.data, 'club_logos')
        
        member_count = 0
        if form.member_count.data:
            try:
                member_count = int(form.member_count.data)
            except ValueError:
                member_count = 0
                
        # Kulüp profili oluştur
        club = Club(
            account_id=account.id,
            name=form.username.data,
            about=form.about.data,
            achievements=form.achievements.data,
            location=form.location.data,
            member_count=member_count,
            phone=form.phone.data,
            email_contact=form.email.data,
            instagram=form.instagram.data,
            twitter=form.twitter.data,
            logo=logo_path  
        )
        club.generate_slug()
        
        db.session.add(club)
        db.session.commit()
        
        flash(
            'Kayıt başarılı! Hesabınız yönetici onayı bekliyor. '
            'Onaylandıktan sonra giriş yapabileceksiniz.',
            'success'
        )
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
def logout():
    
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('main.home'))