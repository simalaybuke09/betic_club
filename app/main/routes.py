
from flask import render_template, request, current_app, jsonify
from app.main import main_bp
from app.models import Post, Club, Account
from app import db
from sqlalchemy import func
from app.utils.weather import get_weather_data


@main_bp.route('/')
def home():
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    
    # Sadece onaylı kulüplerin ve admin'in paylaşımları
    approved_accounts_filter = db.or_(
        Account.account_type == 'admin',
        Account.is_approved == True
    )

    pagination = Post.query.join(Account).filter(
        approved_accounts_filter
    ).order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts = pagination.items
    
    return render_template('main/home.html', 
                         posts=posts, 
                         pagination=pagination)


@main_bp.route('/club/<slug>')
def club_profile(slug):
    
    # Kulübü bul
    club = Club.query.filter_by(slug=slug).first_or_404()
    
    # Kulüp onaylı mı kontrol et
    if not club.account.is_approved:
        from flask import abort
        abort(404)  #404 Not Found
    
    # Kulübün paylaşımları
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    
    pagination = Post.query.filter_by(account_id=club.account_id).order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts = pagination.items
    
    return render_template('main/club_profile.html',
                         club=club,
                         posts=posts,
                         pagination=pagination)


@main_bp.route('/clubs')
def clubs():
    
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'name', type=str)
    per_page = current_app.config.get('CLUBS_PER_PAGE', 12)
    
    # Sadece onaylı kulüpler
    query = Club.query.join(Account).filter(
        Account.is_approved == True
    )
    
    # Sıralama
    if sort_by == 'members':
        query = query.order_by(Club.member_count.desc(), Club.name)
    elif sort_by == 'posts':
        # Post sayısına göre sıralama
        from sqlalchemy import func
        query = query.outerjoin(Post).group_by(Club.id).order_by(
            func.count(Post.id).desc(), Club.name
        )
    elif sort_by == 'newest':
        query = query.order_by(Club.created_at.desc(), Club.name)
    elif sort_by == 'oldest':
        query = query.order_by(Club.created_at.asc(), Club.name)
    else:  # name (varsayılan)
        query = query.order_by(Club.name)
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    clubs = pagination.items
    
    return render_template('main/clubs.html',
                         clubs=clubs,
                         pagination=pagination,
                         sort_by=sort_by)


@main_bp.route('/search')
def search():
    """
    Kulüp arama (AJAX Sayfayı yenilemeden arka planda sunucuyla konuşma tekniğidir JSON döndürür) 
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    # Kulüpleri ara (sadece onaylı)
    clubs = Club.query.join(Account).filter(
        Account.is_approved == True,
        Club.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    # JSON formatında döndür
    results = []
    for club in clubs:
        results.append({
            'name': club.name,
            'slug': club.slug,
            'logo': club.logo,
            'location': club.location,
            'member_count': club.member_count
        })
    
    return jsonify(results)


@main_bp.route('/about')
def about():
    """
    Hakkımızda sayfası (opsiyonel)
    """
    return render_template('main/about.html')


@main_bp.route('/contact')
def contact():
    """
    İletişim sayfası (opsiyonel)
    """
    return render_template('main/contact.html')


@main_bp.route('/api/weather')
def weather_api():
    """
    Hava durumu API endpoint'i
    JSON formatında hava durumu verilerini döndürür
    """
    city = request.args.get('city', 'Trabzon')
    weather_data = get_weather_data(city=city)
    return jsonify(weather_data)