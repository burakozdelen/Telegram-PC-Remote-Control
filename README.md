# 📱 PC Remote Control (Portable EXE)

**Telegram üzerinden bilgisayarınızı tamamen uzaktan kontrol etmenizi sağlayan Python tabanlı, taşınabilir (.exe) bir uzaktan erişim aracı.**

Python kurulumuna gerek yok — sadece indirip çalıştırın!

## 🎯 Proje Hakkında

Bu araç, kendi kişisel bilgisayarınızı uzaktan yönetmek için geliştirilmiş güçlü bir **Remote Administration Tool (RAT)**'tur.  
Açık kaynak bir Python projesinin, kullanım kolaylığı sağlamak amacıyla **PyInstaller** ile derlenmiş taşınabilir EXE sürümüdür.

> ⚠️ **Sadece kendi bilgisayarınızda veya açıkça izin aldığınız sistemlerde kullanın. İzinsiz kullanım yasa dışıdır.**

## ⚡ Özellikler

### 🎥 Medya İşlemleri
- Webcam'den fotoğraf çekme
- Webcam'den video kaydı
- Ortam sesi (mikrofon) kaydı

### 🖥️ Ekran
- Anlık ekran görüntüsü alma (Screenshot)
- Canlı ekran yayını (isteğe bağlı gelecek sürüm)

### 📊 Sistem Bilgileri
- CPU kullanımı & modeli
- RAM kullanımı & toplam bellek
- Disk bilgileri
- Sistem sıcaklık değerleri

### 🎮 Uzaktan Kontrol
- Klavye ile yazı yazdırma
- Fare hareketi ve tıklama kontrolü
- Fare kilidi / serbest bırakma

### 🛡️ Sistem Komutları
- Bilgisayarı kilitleme
- Kapatma
- Yeniden başlatma
- Uyku modu

### ⚙️ Ek Özellikler
- Windows başlangıcına otomatik eklenme (persistence)
- Arka planda sessiz çalışma
- Tek EXE dosyası — bağımlılık yok

## 🚀 Kurulum ve Kullanım

1. **İndirin**  
   `PC_Remote_Control.exe` dosyasını indirin.

2. **Çalıştırın**  
   Mümkünse **Yönetici olarak çalıştırın** (bazı özellikler için gereklidir).

3. **Ayarları Yapın**
   Açılan pencerede:
   - **Telegram Bot Token**: [BotFather](https://t.me/BotFather)'dan aldığınız token
   - **User ID**: Kendi Telegram kullanıcı ID'niz (örnek bot: [@userinfobot](https://t.me/userinfobot))

   > Bot sadece bu ID'ye cevap verecektir (güvenlik önlemi).

4. **Başlatın**  
   "Ayarları Kaydet ve Başlat" butonuna tıklayın.  
   Program sistem tepsisine küçülecek ve Telegram'dan gelen komutları dinlemeye başlayacak.

## ⚠️ Antivirüs Uyarısı

Bu tür araçlar (ekran görüntüsü, kamera, klavye/mouse kontrolü vb.) Windows Defender ve diğer antivirüs yazılımları tarafından **şüpheli** olarak işaretlenebilir.

Bu tamamen normaldir çünkü gerçek RAT'lerde kullanılan Windows API'lerini kullanır.

**Çözüm:**
- Dosyayı/klasörü antivirüs istisnalarına ekleyin
- Kaynak kodunu inceleyip kendiniz derleyebilirsiniz

## 🔒 Güvenlik ve Sorumluluk Reddi

- Bu araç **eğitim ve kişisel kullanım** amacıyla paylaşılmaktadır.
- **Başkalarının bilgisayarında izinsiz kullanmak yasaktır** ve ciddi suç teşkil eder.
- Geliştirici, kötü niyetli kullanımından sorumlu değildir.
