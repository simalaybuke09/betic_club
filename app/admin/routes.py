"""
Admin Routes
Üniversite yönetimi route'ları
"""
import os
from flask import render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.admin.forms import PostForm, EditPostForm, ClubEditForm, FeedbackForm
from app.models import Account, Club, Post, Feedback
from app import db
from openpyxl import Workbook
from io import BytesIO

from app.club.routes import save_image, delete_image, handle_post_images


def admin_required(f):
    """Admin yetkisi kontrolü için decorator"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    
    
    total_clubs = Club.query.count()
    pending_clubs = Account.query.filter_by(account_type='club', is_approved=False).count()
    approved_clubs = Account.query.filter_by(account_type='club', is_approved=True).count()
    
    posts_query = Post.query
    
    total_posts = posts_query.count()
    
    
    recent_posts = posts_query.order_by(Post.created_at.desc()).limit(5).all()
    
    
    recent_applications = Account.query.filter_by(
        account_type='club', 
        is_approved=False
    ).order_by(Account.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_clubs=total_clubs,
                         pending_clubs=pending_clubs,
                         approved_clubs=approved_clubs,
                         total_posts=total_posts,
                         recent_posts=recent_posts,
                         recent_applications=recent_applications)


@admin_bp.route('/clubs/pending')
@login_required
@admin_required
def pending_clubs():
    """Onay bekleyen kulüpler"""
    #URL'deki parametreleri okur
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('CLUBS_PER_PAGE', 12)
    
    pagination = Account.query.filter_by(
        account_type='club',
        is_approved=False
    ).order_by(Account.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    clubs = pagination.items  
    #o sayfaya ait olan verileri (kulüpleri) bir liste olarak alır
    
    return render_template('admin/pending_clubs.html',
                         clubs=clubs,
                         pagination=pagination)
    #bilgileri HTML dosyasına gönderir


@admin_bp.route('/clubs/all')
@login_required
@admin_required
def all_clubs():
    """Tüm kulüpler"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('CLUBS_PER_PAGE', 12)
    
    
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    query = Club.query.join(Account)
    
    #HTML den gelen verileri tabloda Arama
    if search:
        query = query.filter(Club.name.ilike(f'%{search}%'))  #Büyük/küçük harf duyarlılığını kaldırır
    
    # Durum filtresi
    if status == 'approved':
        query = query.filter(Account.is_approved == True)
    elif status == 'pending':
        query = query.filter(Account.is_approved == False)
    
    pagination = query.order_by(Club.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    clubs = pagination.items
    
    return render_template('admin/all_clubs.html',
                         clubs=clubs,
                         pagination=pagination,
                         status=status,
                         search=search)

@admin_bp.route('/clubs/download/<file_type>')
@login_required
@admin_required
def download_clubs(file_type):
    """Filtrelenmiş kulüp listesini PDF veya Excel olarak indirir."""
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    query = Club.query.join(Account)
    
    if search:
        query = query.filter(Club.name.ilike(f'%{search}%'))
    
    if status == 'approved':
        query = query.filter(Account.is_approved == True)
    elif status == 'pending':
        query = query.filter(Account.is_approved == False)
        
    clubs = query.order_by(Club.name).all()

    if file_type == 'excel':
        wb = Workbook()  #Bellekte boş bir Excel çalışma kitabı oluşturur.
        ws = wb.active   #Excel'deki ilk sayfayı (Sheet) seçer.
        ws.title = "Kulüpler"
        ws.append(['ID', 'Kulüp Adı', 'Slug', 'E-posta', 'Onay Durumu', 'Üye Sayısı', 'Konum', 'Telefon', 'Oluşturulma Tarihi'])

        for club in clubs:
            status_text = 'Onaylı' if club.account.is_approved else 'Bekliyor'
            ws.append([club.id, club.name, club.slug, club.account.email, status_text, club.member_count or 0, club.location, club.phone, club.created_at.strftime('%Y-%m-%d %H:%M')])
        
        buffer = BytesIO()  #hard diskine kaydetmek yerine geçici olarak RAM üzerinde tutar.
        wb.save(buffer)
        buffer.seek(0)  #Dosyanın yazılması bittiğinde okuma imlecini dosyanın en başına getirir

        return Response(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': 'attachment;filename=kulupler.xlsx'})
        #Bu sefer bir HTML sayfası değil, bir dosya döndür -response
        #Mimetype: İnternet üzerindeki dosya türlerini tanımla
    flash('Geçersiz dosya türü.', 'danger')
    return redirect(url_for('admin.all_clubs'))


@admin_bp.route('/club/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_club(id):
    """Kulübü onayla"""
    account = Account.query.get_or_404(id)
    
    if account.account_type != 'club':
        flash('Bu hesap bir kulüp değil.', 'danger')
        return redirect(url_for('admin.pending_clubs'))
    
    account.is_approved = True
    db.session.commit()
    
    flash(f'{account.club.name} kulübü onaylandı!', 'success')
    return redirect(url_for('admin.pending_clubs'))


@admin_bp.route('/club/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_club(id):
    """Kulüp başvurusunu reddet"""
    account = Account.query.get_or_404(id)
    
    if account.account_type != 'club':
        flash('Bu hesap bir kulüp değil.', 'danger')
        return redirect(url_for('admin.pending_clubs'))
    
    account.is_approved = False
    db.session.commit()
    
    flash(f'{account.club.name} kulübünün onayı kaldırıldı.', 'warning')
    return redirect(url_for('admin.all_clubs'))


@admin_bp.route('/club/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_club(id):
    """Kulübü sil"""
    account = Account.query.get_or_404(id)
    
    if account.account_type != 'club':
        flash('Bu hesap bir kulüp değil.', 'danger')
        return redirect(url_for('admin.all_clubs'))
    
    club_name = account.club.name if account.club else account.username
    
    # Kulüp logosunu sil
    if account.club and account.club.logo:
        delete_image(account.club.logo)
    
    
    # Paylaşım resimlerini sil
    for post in account.posts.all():
        for img_path in post.get_images():
            delete_image(img_path)
    
    db.session.delete(account)
    db.session.commit()
    
    flash(f'{club_name} kulübü silindi.', 'success')
    return redirect(url_for('admin.all_clubs'))


@admin_bp.route('/club/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_club(id):
    """Kulüp bilgilerini düzenle"""
    account = Account.query.get_or_404(id)
    
    if account.account_type != 'club' or not account.club:
        flash('Kulüp bulunamadı.', 'danger')
        return redirect(url_for('admin.all_clubs'))
    
    club = account.club
    form = ClubEditForm()
    
    if form.validate_on_submit():
        club.name = form.name.data
        club.about = form.about.data
        club.achievements = form.achievements.data
        club.location = form.location.data
        
        # Üye sayısı
        try:
            club.member_count = int(form.member_count.data) if form.member_count.data else 0
        except ValueError:
            club.member_count = 0
        
        club.phone = form.phone.data
        club.email_contact = form.email_contact.data
        club.instagram = form.instagram.data
        club.twitter = form.twitter.data
        club.linkedin = form.linkedin.data
        club.facebook = form.facebook.data
        club.website = form.website.data
        
        # Logo güncelle
        if form.logo.data:
            # Eski logoyu sil
            if club.logo:
                delete_image(club.logo)
            
            # Yeni logoyu kaydet
            logo_path = save_image(form.logo.data, 'club_logos')
            if logo_path:
                club.logo = logo_path
        
        # Slug güncelle
        club.generate_slug()
        
        db.session.commit()
        flash('Kulüp bilgileri güncellendi!', 'success')
        return redirect(url_for('admin.all_clubs'))
    
    # Formu doldur
    if request.method == 'GET':
        form.name.data = club.name
        form.about.data = club.about
        form.achievements.data = club.achievements
        form.location.data = club.location
        form.member_count.data = str(club.member_count) if club.member_count else '0'
        form.phone.data = club.phone
        form.email_contact.data = club.email_contact
        form.instagram.data = club.instagram
        form.twitter.data = club.twitter
        form.linkedin.data = club.linkedin
        form.facebook.data = club.facebook
        form.website.data = club.website
    
    return render_template('admin/edit_club.html', form=form, club=club)


@admin_bp.route('/posts')
@login_required
@admin_required
def all_posts():
    """Tüm paylaşımları listele (feedbackler hariç)"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts = pagination.items
    
    return render_template('admin/all_posts.html',
                         posts=posts,
                         pagination=pagination)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_post():
    """Yeni paylaşım oluştur"""
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
        return redirect(url_for('admin.all_posts'))
    
    return render_template('admin/create_post.html', form=form)


@admin_bp.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(id):
    """Paylaşımı düzenle"""
    post = Post.query.get_or_404(id)
    form = EditPostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        
        # Yeni resimler yüklendiyse
        existing_images = post.get_images() if post.image else []
        if form.images.data:
            image_paths = handle_post_images(form.images.data)
            #her bir resmi sunucuya kaydeder,isimlerini benzersiz yapar dosya yolunu döndürür
        
        # Yeni resimler varsa ekle
        if image_paths:
            all_images = existing_images + image_paths
            post.image = ','.join(all_images)
        
        db.session.commit()
        flash('Paylaşım güncellendi!', 'success')
        return redirect(url_for('admin.all_posts'))
    
    return render_template('admin/edit_post.html', form=form, post=post)


@admin_bp.route('/post/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(id):
    """Paylaşımı sil"""
    post = Post.query.get_or_404(id)
    
    # Tüm resimleri sil
    if post.image:
        for img_path in post.get_images():
            delete_image(img_path)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Paylaşım silindi.', 'success')
    return redirect(url_for('admin.all_posts'))


@admin_bp.route('/feedback/new', methods=['GET', 'POST'])
@login_required
@admin_required
def send_feedback():
    """Kulübe feedback (geri bildirim) gönder"""
    form = FeedbackForm()
    
    # Onaylı kulüpleri form'a ekle
    approved_clubs = Club.query.join(Account).filter(
        Account.is_approved == True
    ).order_by(Club.name).all()
    
    form.club_id.choices = [(club.id, club.name) for club in approved_clubs]
    
    if form.validate_on_submit():
        club = Club.query.get_or_404(form.club_id.data)
        
        # Feedback'i Feedback modeli olarak kaydet
        feedback = Feedback(
            sender_id=current_user.id,
            club_id=club.id,
            title=form.title.data,
            content=form.content.data
        )
        
        try:
            db.session.add(feedback)
            db.session.commit()
            flash(f'{club.name} kulübüne geri bildirim gönderildi!', 'success')
            return redirect(url_for('admin.all_feedbacks'))
        except Exception as e:
            db.session.rollback()
            flash('Geri bildirim gönderilirken bir hata oluştu.', 'danger')
            current_app.logger.error(f"Feedback error: {str(e)}")
    
    return render_template('admin/send_feedback.html', form=form, clubs=approved_clubs)


@admin_bp.route('/feedbacks')
@login_required
@admin_required
def all_feedbacks():
    """Tüm feedback'leri listele"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    
    try:
        # Sadece feedback'leri getir
        pagination = Feedback.query.order_by(Feedback.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        feedbacks = pagination.items
        
        return render_template('admin/all_feedbacks.html',
                             feedbacks=feedbacks,
                             pagination=pagination)
    except Exception as e:
        current_app.logger.error(f"All feedbacks error: {str(e)}")
        flash('Geri bildirimler yüklenirken bir hata oluştu.', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/feedback/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_feedback(id):
    """Feedback sil"""
    feedback = Feedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Geri bildirim silindi.', 'success')
    return redirect(url_for('admin.all_feedbacks'))
