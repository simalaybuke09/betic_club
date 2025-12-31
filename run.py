
import os
from app import create_app, db
from app.models import Account, Club, Post, Message, Feedback

# Flask uygulamasını oluştur
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    Flask shell için context oluştur
    Kullanım: flask shell
    """
    return {
        'db': db,
        'Account': Account,
        'Club': Club,
        'Post': Post,
        'Message': Message,
        'Feedback': Feedback
    }

#Fonksiyonu normal bir Python fonksiyonu olmaktan çıkarır
# terminalden flask create-admin yazılarak çalıştırılan bir komuta dönüştürür.
@app.cli.command()
def create_admin():
    """
    Admin hesabı oluştur
    Kullanım: flask create-admin
    """
   
    
    admin = Account.query.filter_by(account_type='admin').first()
    if admin:
        print("❌ Admin hesabı zaten mevcut!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        return
    
   
    admin = Account(
        username=app.config['ADMIN_USERNAME'],
        email=app.config['ADMIN_EMAIL'],
        account_type='admin',
        is_approved=True
    )
    admin.set_password(app.config['ADMIN_PASSWORD'])
    
    db.session.add(admin)
    db.session.commit()
    
    print("✅ Admin hesabı başarıyla oluşturuldu!")
    print(f"   Username: {admin.username}")
    print(f"   Email: {admin.email}")
    print(f"   Password: {app.config['ADMIN_PASSWORD']}")
    print("\n⚠️  Güvenlik için admin şifresini değiştirmeyi unutmayın!")


@app.cli.command()
def create_sample_data():
    """
    Örnek test verileri oluştur
    Kullanım: flask create-sample-data
    """
    print("📝 Örnek veriler oluşturuluyor...")
    
    
    club_account1 = Account(
        username='yazilim-kulubu',
        email='yazilim@uni.edu.tr',
        account_type='club',
        is_approved=True
    )
    club_account1.set_password('12345')
    db.session.add(club_account1)
    db.session.flush()#veriyi veritabanına gönderir ama henüz kalıcı yapmaz
                     #id almak için
    
    club1 = Club(
        account_id=club_account1.id,
        name='Yazılım Kulübü',
        about='Yazılım ve teknoloji odaklı projeler geliştiren öğrenci topluluğu',
        achievements='2024 Hackathon Birinciliği, Google Developer Student Club',
        location='Mühendislik Fakültesi A Blok',
        member_count=150,
        phone='0555 123 45 67',
        email_contact='yazilim@uni.edu.tr',
        instagram='yazilimkulubu',
        twitter='yazilimkulubu'
    )
    club1.generate_slug()
    db.session.add(club1)
    
    club_account2 = Account(
        username='muzik-kulubu',
        email='muzik@uni.edu.tr',
        account_type='club',
        is_approved=False  
    )
    club_account2.set_password('12345')
    db.session.add(club_account2)
    db.session.flush()
    
    club2 = Club(
        account_id=club_account2.id,
        name='Müzik Kulübü',
        about='Müzik severleri bir araya getiren kulüp',
        location='Güzel Sanatlar Fakültesi',
        member_count=80,
        email_contact='muzik@uni.edu.tr'
    )
    club2.generate_slug()
    db.session.add(club2)
    
    db.session.commit()
    db.session.flush()
   
    # Örnek paylaşımlar
    admin = Account.query.filter_by(account_type='admin').first()
    
    post1 = Post(
        account_id=admin.id,
        title='Bahar Şenliği Duyurusu',
        content='Üniversitemizin geleneksel Bahar Şenliği 15 Mayıs tarihinde düzenlenecektir. Tüm öğrencilerimizi bekliyoruz!'
    )
    
    post2 = Post(
        account_id=club_account1.id,
        title='Hackathon 2024 Kayıtları Başladı',
        content='24 saatlik hackathon etkinliğimiz için kayıtlar başlamıştır. Ödüllü yarışmaya katılmak için son kayıt tarihi 1 Haziran.'
    )
    
    # Örnek Geri Bildirim (Feedback)
    feedback = Feedback(
        sender_id=admin.id,
        club_id=club1.id,
        title='Etkinlik Tebriği',
        content='Düzenlediğiniz hackathon çok başarılıydı, tebrik ederiz.'
    )
    
    db.session.add_all([post1, post2, feedback])
    db.session.commit()
    
    print("✅ Örnek veriler oluşturuldu!")
    print("\n📋 Oluşturulan hesaplar:")
    print("   Admin: admin / admin123")
    print("   Kulüp 1: yazilim-kulubu / 12345 (Onaylı)")
    print("   Kulüp 2: muzik-kulubu / 12345 (Onay bekliyor)")


if __name__ == '__main__':
    #Bu dosya doğrudan çalıştırılıyorsa şu kodu başlat
    app.run(debug=True, host='0.0.0.0', port=5000)