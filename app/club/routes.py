"""
Club Routes
Kulüp paneli route'ları
"""
import os
from functools import wraps
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_
from app.club import club_bp
from app.club.forms import (PostForm, EditPostForm, ClubProfileForm, MessageForm)
from app.models import Post, Club, Message, Feedback, Account
from app import db
from werkzeug.utils import secure_filename
import uuid


#f çalışmadan önce yetki kontrolü yapar
def club_required(f):
    """Kulüp yetkisi kontrolü için decorator"""
    #Eğer wraps kullanmazsak flask parametre olarak aldığı f artık kendi adıyla çağrılamaz bunu engellemek için
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_club():
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.home'))
        if not current_user.is_approved:
            flash('Hesabınız henüz onaylanmadı. Lütfen yönetimin onayını bekleyin.', 'warning')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


def save_image(file, folder):
    """Resim kaydetme yardımcı fonksiyonu"""
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex[:10]}_{filename}"
        
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return f"{folder}/{unique_filename}"
    return None


def delete_image(image_path):
    """Resim silme yardımcı fonksiyonu"""
    if image_path:
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception as e:
                print(f"Resim silinirken hata: {e}")


def handle_post_images(files):
    """Formdan gelen resim listesini işler ve kaydeder"""
    image_paths = []
    for img_file in files:
        if img_file and img_file.filename:
            img_path = save_image(img_file, 'post_images')
            if img_path:
                image_paths.append(img_path)
    return image_paths


@club_bp.route('/dashboard')
@login_required
@club_required
def dashboard():
    """Kulüp ana paneli"""
    club = current_user.club
    
    # Kulübün paylaşımları (feedback'ler hariç)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    
    # Filtreleme kriterleri (Mesajlar ve Feedback'ler hariç)
    # Yeni veritabanında Post tablosunda sadece paylaşımlar var
    posts_query = Post.query.filter_by(account_id=current_user.id)
    
    pagination = posts_query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    posts = pagination.items
    total_posts = pagination.total
    
    # Bu kulübe gönderilen feedback'ler
    feedbacks = club.feedbacks.order_by(Feedback.created_at.desc()).limit(5).all()
    feedback_count = club.feedbacks.count()
    
    return render_template('club/dashboard.html',
                         club=club,
                         posts=posts,
                         pagination=pagination,
                         total_posts=total_posts,
                         feedbacks=feedbacks,
                         feedback_count=feedback_count)


@club_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@club_required
def edit_profile():
    """Kulüp profilini düzenle"""
    club = current_user.club
    form = ClubProfileForm(obj=club)
    
    if form.validate_on_submit():
        # Kulüp adı değiştirildi mi kontrol et
        if form.name.data != club.name:
            # Başka kulüp bu ismi kullanıyor mu?
            existing_club = Club.query.filter_by(name=form.name.data).first()
            if existing_club and existing_club.id != club.id:
                flash('Bu kulüp adı zaten kullanılıyor.', 'danger')
                return redirect(url_for('club.edit_profile'))
            
            club.name = form.name.data
            club.generate_slug()
        
        # Logo güncelle
        if form.logo.data:
            # Eski logoyu sil
            if club.logo:
                delete_image(club.logo)
            
            # Yeni logoyu kaydet
            logo_path = save_image(form.logo.data, 'club_logos')
            if logo_path:
                club.logo = logo_path
        
        # Diğer bilgileri güncelle
        club.about = form.about.data
        club.achievements = form.achievements.data
        club.location = form.location.data
        
        # Üye sayısı
        try:
            club.member_count = int(form.member_count.data) if form.member_count.data else 0
        except ValueError:
            club.member_count = 0
        
        # İletişim bilgileri
        club.phone = form.phone.data
        club.email_contact = form.email_contact.data
        
        # Sosyal medya
        club.instagram = form.instagram.data
        club.twitter = form.twitter.data
        club.linkedin = form.linkedin.data
        club.facebook = form.facebook.data
        club.website = form.website.data
        
        db.session.commit()
        flash('Profil başarıyla güncellendi!', 'success')
        return redirect(url_for('club.dashboard'))
    
    return render_template('club/edit_profile.html', form=form, club=club)


@club_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
@club_required
def create_post():
    """Yeni paylaşım oluştur"""
    club = current_user.club
    form = PostForm()
    
    if form.validate_on_submit():
        # Resimleri kaydet (çoklu)
        image_paths = []
        if form.images.data:
            image_paths = handle_post_images(form.images.data)
        
        image_str = ','.join(image_paths) if image_paths else None
        
        # Paylaşımı oluştur
        post = Post(
            account_id=current_user.id,
            title=form.title.data,
            content=form.content.data,
            image=image_str
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('Paylaşım başarıyla oluşturuldu!', 'success')
        return redirect(url_for('club.dashboard'))
    
    return render_template('club/create_post.html', form=form, club=club)


@club_bp.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@club_required
def edit_post(id):
    """Paylaşımı düzenle"""
    club = current_user.club
    post = Post.query.get_or_404(id)
    
    # Bu kulübün paylaşımı mı kontrol et
    if post.account_id != current_user.id:
        flash('Bu paylaşımı düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('club.dashboard'))
    
    form = EditPostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        
        # Yeni resimler yüklendiyse
        image_paths = []
        existing_images = post.get_images() if post.image else []
        if form.images.data:
            image_paths = handle_post_images(form.images.data)
        
        # Yeni resimler varsa ekle
        if image_paths:
            all_images = existing_images + image_paths
            post.image = ','.join(all_images)
        
        db.session.commit()
        flash('Paylaşım güncellendi!', 'success')
        return redirect(url_for('club.dashboard'))
    
    return render_template('club/edit_post.html', form=form, post=post, club=club)


@club_bp.route('/post/<int:id>/delete', methods=['POST'])
@login_required
@club_required
def delete_post(id):
    """Paylaşımı sil"""
    post = Post.query.get_or_404(id)
    
    # Bu kulübün paylaşımı mı kontrol et
    if post.account_id != current_user.id:
        flash('Bu paylaşımı silme yetkiniz yok.', 'danger')
        return redirect(url_for('club.dashboard'))
    
    # Tüm resimleri sil
    if post.image:
        for img_path in post.get_images():
            delete_image(img_path)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Paylaşım silindi.', 'success')
    return redirect(url_for('club.dashboard'))

# app/club/routes.py içine eklenecek kodlar:

@club_bp.route('/messages')
@login_required
@club_required
def messages():
    """Sohbet listesi (Son konuşulanlar)"""
    my_id = current_user.id
    
    # Mesajları konuşmalara göre grupla
    chats = {}
    
    # Tüm mesajlarımı getir (Gelen ve Giden)
    all_messages = Message.query.filter(
        (Message.sender_id == my_id) | (Message.recipient_id == my_id)
    ).order_by(Message.created_at.desc()).all()
    
    for msg in all_messages:
        # Konuşulan kişiyi belirle
        partner_id = msg.recipient_id if msg.sender_id == my_id else msg.sender_id
        
        if partner_id not in chats:
            partner_account = Account.query.get(partner_id)
            # Sadece kulüplerle olan mesajlaşmaları listele (veya admin)
            if partner_account and partner_account.club:
                chats[partner_id] = {
                    'club': partner_account.club,
                    'last_msg': msg
                }
            
    # Tarihe göre sırala (En yeni en üstte)
    sorted_chats = sorted(chats.values(), key=lambda x: x['last_msg'].created_at, reverse=True)
    
    return render_template('club/messages.html', chats=sorted_chats)

@club_bp.route('/chat/<slug>', methods=['GET', 'POST'])
@login_required
@club_required
def chat(slug):
    """Sohbet ekranı"""
    target_club = Club.query.filter_by(slug=slug).first_or_404()
    target_id = target_club.account_id
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            msg = Message(
                sender_id=current_user.id,
                recipient_id=target_id,
                content=content
            )
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for('club.chat', slug=slug))
    
    # Mesaj geçmişini getir (Gelenler ve Gidenler)
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == target_id)) |
        ((Message.sender_id == target_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.created_at).all()
    
    # Okundu olarak işaretle
    unread = Message.query.filter_by(recipient_id=current_user.id, sender_id=target_id, is_read=False).all()
    if unread:
        for m in unread: m.is_read = True
        db.session.commit()
    
    return render_template('club/chat.html', target_club=target_club, messages=messages)

@club_bp.route('/message/new', methods=['GET', 'POST'])
@login_required
@club_required
def send_message():
    """Yeni mesaj gönder"""
    form = MessageForm()
    # Kendisi hariç diğer kulüpleri listele
    clubs = Club.query.filter(Club.id != current_user.club.id).order_by(Club.name).all()
    form.recipient_id.choices = [(c.id, c.name) for c in clubs]

    if form.validate_on_submit():
        target_club = Club.query.get(form.recipient_id.data)
        if target_club:
            msg = Message(
                sender_id=current_user.id,
                recipient_id=target_club.account_id,
                content=form.content.data
            )
            db.session.add(msg)
            db.session.commit()
            flash('Mesajınız gönderildi.', 'success')
            return redirect(url_for('club.chat', slug=target_club.slug))
    
    return render_template('club/send_message.html', form=form)
