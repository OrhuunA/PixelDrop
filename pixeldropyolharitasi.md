# PixelDrop — Geliştirme Yol Haritası

Bu dosya iki bölümden oluşuyor: **repo tarafındaki iyileştirmeler** (release
dışında) ve **eklenebilecek özellikler**. Her madde tek başına bir commit /
bir günlük push olacak şekilde ayrılmış durumda.

---

## 1. Repo Hijyeni

Toplam süresi kısa, görünürlüğe etkisi en büyük olan kısım. Repoya ilk kez
giren birinin ilk 10 saniyede gördüğü şeyler.

### 1.1 About bölümü

Şu an "No description, website, or topics provided" yazıyor. Repo başlığının
sağındaki dişli ikonundan doldurulur.

- **Description:** Tek cümle, ne yaptığı hemen anlaşılsın.
  Örnek: `Ekranda yaşayan piksel-art su damlası maskotuyla su içmeyi hatırlatan hafif Windows masaüstü aracı`
- **Topics:** `python`, `tkinter`, `windows`, `desktop-widget`, `pixel-art`,
  `health`, `reminder`, `system-tray`, `pystray`, `productivity`
- **Website:** Boş bırakılabilir; ilerideki GitHub Pages tanıtım sayfası
  buraya bağlanır.

Topic'ler GitHub içi aramada bulunabilirliği doğrudan etkiliyor. Şu an repo
hiçbir konu listesinde görünmüyor.

### 1.2 Sosyal önizleme görseli

Settings → General → Social preview. Yüklenmezse paylaşılan linklerde
otomatik oluşturulan gri kutu çıkıyor. Maskotun büyük hâli + isim + tek
satır açıklama içeren 1280×640 bir görsel yeterli. Maskotu zaten Pillow ile
çizdiğin için bu görseli üreten küçük bir script yazmak da mümkün.

### 1.3 Commit geçmişi

Şu an 3 commit var. Geriye dönük düzeltilecek bir şey yok, ancak bundan
sonrası için:

- Her özellik/düzeltme ayrı commit
- Anlamlı mesajlar — tercihen [Conventional Commits](https://www.conventionalcommits.org/):
  `feat: ml bazlı miktar takibi`, `fix: gece yarısı sayaç sıfırlanmıyordu`,
  `refactor: UI katmanını ayrı modüle taşı`
- Bu format ileride otomatik CHANGELOG üretmeyi de mümkün kılar

### 1.4 Dosya adları

`kur_ve_test_et.bat` ve `build_exe.bat` — biri Türkçe, biri İngilizce. Tek
dile sabitle. Öneri: `setup.bat` / `build.bat`, ya da her ikisi de Türkçe.
Küçük bir detay ama repo genelinde tutarlılık hissi veriyor.

### 1.5 Issue şablonları

`.github/ISSUE_TEMPLATE/` altına `bug_report.md` ve `feature_request.md`.
Bug şablonunda Windows sürümü, PixelDrop sürümü, `config.json` içeriği ve
adımlar sorulsun. Kullanıcı gelmese bile repo'nun bakımlı olduğunu gösteren
bir sinyal.

### 1.6 CHANGELOG.md

Sürüm sürüm neyin değiştiği. Şu ana kadarki özellikleri `v1.0.0` altına
toplayıp bundan sonrasını eklemeye devam etmek yeterli.

---

## 2. README İyileştirmeleri

Repo'nun asıl vitrini burası ve şu an düzeltilecek birkaç somut nokta var.

### 2.1 Türkçe karakterler

README baştan sona diakritiksiz: "hatirlatan", "ozellikler", "surukle",
"gunluk". Muhtemelen encoding derdinden kaçınmak için ama okurken
profesyonellik hissini düşürüyor. GitHub UTF-8'i sorunsuz gösteriyor,
düzgün Türkçe yazılabilir.

### 2.2 İki dilli yapı

`README.md` (Türkçe) + `README.en.md` (İngilizce), her ikisinin en üstünde
karşılıklı link. Uygulamanın kendisi zaten iki dilli — README'nin tek dilde
kalması onu yurt dışı görünürlüğünden koparıyor. Yüksek lisans başvurusu
düşünüyorsan İngilizce versiyon ayrıca önemli.

### 2.3 İndirme bölümünü en üste al

Şu anki sıralama: açıklama → ekran görüntüsü → özellikler → `pip install`.
Yani repoya giren biri önce Python kurulumu görüyor.

Doğru sıralama:

1. Başlık + tek cümle açıklama
2. GIF / ekran görüntüsü
3. **İndir** (zip linki, büyük ve görünür)
4. Özellikler
5. Kullanım
6. Geliştirme ortamı (`pip install ...`)
7. Mimari notları

### 2.4 SmartScreen uyarısı için açıklama

İmzasız exe'nin Windows tarafından engellenmesi normal ve bilinen bir
durum — kod imzalama sertifikası olmadan kaçınılmaz. Zip çözümü doğru bir
geçici yol, ancak README'de bir bölüm olarak açıklanmalı:

- Neden bu uyarının çıktığı (kod imzalama sertifikası yok, ticari
  sertifikalar yıllık ücretli)
- Uyarıyı geçme adımları ("Daha fazla bilgi" → "Yine de çalıştır")
- Kaynak kodun açık olduğu ve isteyenin `build.bat` ile kendisinin
  derleyebileceği notu

Bu bölüm olmadan indiren kullanıcıların çoğu uyarıyı görüp vazgeçiyor.
Açıklama, indirenlerin devam etme oranını ciddi biçimde arttırıyor.

### 2.5 Görsel içerik

Mevcut `mascot_states.png` iyi ama yetersiz. Eklenecekler:

- **Masaüstü ekran görüntüsü:** Widget'ın gerçek bir masaüstünde, diğer
  pencerelerin üstünde nasıl durduğu — boyut algısı için şart
- **GIF (en önemlisi):** Kademeli kuruma geçişi → hatırlatma → tıklama →
  sevinme animasyonu. 5-8 saniye yeterli. Bu tür bir uygulamada animasyonlu
  önizleme, metnin tamamından daha ikna edici
- **Ayarlar penceresi** ve **7 günlük grafik** ekran görüntüsü
- **Tepsi menüsü** açık hâlde bir kare

ScreenToGif veya ShareX ile kaydedilebilir. `docs/img/` altına koy.

### 2.6 Rozetler

Başlığın altına: lisans, Python sürümü, platform (Windows), son sürüm,
indirme sayısı. Shields.io ile üretilir. Süs gibi görünüyor ama repo'nun
"bakımlı" hissini belirgin şekilde arttırıyor.

---

## 3. Kod Kalitesi ve Mimari

### 3.1 Modüllere ayırma

Her şey tek `main.py` içinde: UI, Pillow çizimleri, zamanlama, config
yönetimi, tepsi ikonu, `STRINGS` dil sözlüğü, Windows API çağrıları. Şu an
çalışıyor ancak özellik ekledikçe dosya sürekli şişecek ve bir noktada
üzerinde çalışmak zorlaşacak.

Önerilen yapı:

```
pixeldrop/
├── __init__.py
├── __main__.py          # giriş noktası
├── config.py            # config.json okuma/yazma, migration, varsayılanlar
├── core/
│   ├── timer.py         # hatırlatma zamanlaması, erteleme
│   ├── tracker.py       # günlük sayaç, hedef, seri, geçmiş
│   └── idle.py          # GetLastInputInfo sarmalayıcı
├── ui/
│   ├── widget.py        # ana maskot penceresi
│   ├── settings.py      # ayarlar penceresi
│   ├── tray.py          # pystray entegrasyonu
│   └── mascot.py        # Pillow ile piksel-art çizim
├── notify.py            # winotify + winsound
└── i18n.py              # STRINGS sözlüğü
```

Ayırmanın asıl faydası: `core/` altındaki mantık UI'dan bağımsız hâle
gelince test edilebilir oluyor (bkz. bölüm 4).

### 3.2 Dilleri dışarı çıkarma

`STRINGS` sözlüğü koddan `i18n/tr.json` ve `i18n/en.json` dosyalarına
taşınabilir. Üçüncü bir dil eklemek kod değişikliği gerektirmez hâle gelir
ve dışarıdan katkı almak kolaylaşır.

### 3.3 Ayarlar penceresi dil değişimi

README'de şu not var: dil değişince ayarlar penceresi yeniden açılarak
güncelleniyor. Widget metinleri dinamik okurken ayarların pencere
kapatıp açması tutarsız. Etiket referanslarını bir sözlükte tutup
`configure(text=...)` ile güncellemek daha temiz bir çözüm.

### 3.4 Tip ipuçları ve linting

`ruff` + `mypy` ekle, `pyproject.toml` ile yapılandır. Kod kalitesi
denetimi yaptığını gösterir ve büyüyen dosyada hataları erken yakalar.

### 3.5 Sürüm bilgisi

Kod içinde tek bir `__version__` tanımı, ayarlar penceresinde ve tepsi
menüsünde görünsün. Kullanıcının hangi sürümü kullandığını bilmesi bug
raporu için gerekli.

---

## 4. Test

Test yazmaya ilgin olduğu için burada iyi bir eşleşme var: uygulamadaki en
sinsi hatalar elle test edilmesi en zor yerlerde.

### 4.1 Elle test edilmesi imkânsıza yakın olan senaryolar

- **Gün dönümü:** Gece yarısı geçildiğinde sayacın sıfırlanması. Elle test
  etmek için gece yarısını beklemek gerekiyor
- **Seri hesabı:** Hedef tutturulan gün → seri +1, tutturulamayan gün →
  sıfırlanma. Ayrıca uygulamanın hiç açılmadığı günlerin doğru işlenmesi
- **Geçmiş budama:** 14 günlük pencere kayarken eski kayıtların silinmesi
- **Config migration:** Eski `SuIcmeHatirlatici` klasöründen taşıma. Bir kez
  çalışan bir kod, bozulduğunda kimse fark etmiyor
- **Bozuk config:** `config.json` yarım yazılmış, silinmiş veya elle
  bozulmuşsa uygulama çökmeden varsayılanlara dönmeli
- **Erteleme mantığı:** Üst üste erteleme, ertelemeden sonra su içme,
  duraklatma sırasında erteleme

### 4.2 Uygulama

`core/` modüllerini saf fonksiyon hâline getir (bugünün tarihini parametre
olarak al, `datetime.now()` çağırma), sonra pytest ile test et. Zamana
bağımlı testlerde `freezegun` kullanılabilir.

Hedef: `pytest` ile çalışan 15-25 test. Sonrasında bir GitHub Action ile
her push'ta otomatik çalıştır.

---

## 5. Eklenebilecek Özellikler

Mevcut hâlde şunlar zaten var: seri takibi, boşta otomatik duraklama, hızlı
erteleme, 7 günlük geçmiş, kademeli kuruma, iki dil, tepsi entegrasyonu,
başlangıçta çalıştırma. Aşağıdakiler bunların üzerine gelecek olanlar.

### 5.1 Yüksek öncelik — kullanımı doğrudan etkileyenler

**Gerçek miktar takibi (ml)**
Şu an birim "bardak" ve herkesin bardağı farklı. Kendi kaplarını tanımlama:
`Bardak 200ml`, `Matara 750ml`, `Kupa 330ml`. Widget'ta tek tık varsayılan
kabı ekler, sağ tık kap listesi açar. Günlük hedef ml cinsinden tutulur
(varsayılan 2000ml). Bu, uygulamayı basit bir sayaçtan gerçek bir takip
aracına çeviren en önemli değişiklik.

**Yanlış tıklamayı geri alma**
Sürükle-bırak ile tek tık arasında karışma ihtimali var. Yanlışlıkla eklenen
kaydı geri almanın yolu yoksa sayaç bozuluyor ve kullanıcı verisine
güvenmeyi bırakıyor. Su içildikten sonra 10 saniye boyunca widget'ta küçük
bir geri alma ikonu belirsin, ayrıca ayarlar penceresinden son kaydı silme
seçeneği olsun.

**Bildirim üzerinden kayıt**
`winotify` toast bildirimlerine buton eklemeyi destekliyor. Bildirimde
doğrudan "İçtim" ve "Ertele" butonları olsun. Kullanıcının widget'a gitmesi
gerekmeden kayıt girmesi, bu tür uygulamalarda terk oranını en çok düşüren
tek özellik.

**Sessiz saatler**
Boşta duraklama var ancak saat bazlı sessizlik yok. Gece bilgisayar başında
oturan biri bildirim almaya devam ediyor. `23:00 – 08:00` gibi bir aralık
tanımlanabilsin, bu aralıkta hatırlatma gelmesin ve sabah ilk hatırlatma
uyanma saatinde yapılsın.

### 5.2 Orta öncelik — deneyimi zenginleştirenler

**Maskot çeşitleri**
Piksel-art çalışma zamanında Pillow ile çiziliyor; yani ikinci bir karakter
eklemek harici görsel dosyası eklemekten daha kolay. Kaktüs (kuruyunca
dikenleri sarkar), kedi, çaydanlık, kar tanesi. Görsel çeşitlilik bu tür
uygulamalarda paylaşılma ve tavsiye edilme sebebi.

**Tema / renk paleti**
Koyu ve açık masaüstü arka planlarına göre kontrast ayarı, ayrıca birkaç
hazır renk paleti. Şeffaf pencere kullandığın için açık renkli duvar
kâğıdında maskot okunmuyor olabilir — test edilmeye değer bir nokta.

**Genişletilmiş istatistikler**
Mevcut 7 günlük grafiğin yanına: aylık görünüm, haftanın hangi günü daha
iyi/kötü olduğun, günün hangi saatlerinde içtiğin (saat bazlı dağılım), en
uzun seri rekoru. Veri zaten `history` alanında duruyor, sadece
görselleştirilmesi gerekiyor.

**Dışa aktarma**
`config.json` içindeki geçmişi CSV veya JSON olarak dışa aktarma. Küçük bir
iş ancak "verim bende kalıyor" hissi veriyor ve README'de iyi duruyor.

**Ses seçenekleri**
Şu an tek `winsound` bip'i var. Birkaç hazır ses (damla sesi, zil, yumuşak
ton) ve kendi `.wav` dosyanı seçme imkânı. Ayrıca ses seviyesi ayarı.

**Kutlama efekti**
Günlük hedefe ulaşıldığında sadece sevinme animasyonu yerine kısa bir
konfeti/kabarcık efekti. Görsel ödül, seri devamlılığını destekleyen şey.

**İlk açılış sihirbazı**
Uygulama ilk kez açıldığında 3 adımlık kısa bir karşılama: hedef belirleme,
kap tanımlama, widget konumu seçme. Yeni kullanıcının ayarları hiç açmadan
doğru kurulmuş bir uygulamaya sahip olmasını sağlar.

### 5.3 Düşük öncelik — uzun vadeli fikirler

**Bağlama duyarlı hedef**
Hava sıcaklığını bir API'den çekip sıcak günlerde günlük hedefi otomatik
arttırma. Ayrıca widget'a "spor yaptım" butonu ekleyip o güne ek hedef
tanımlama.

**Başarımlar (achievements)**
7 gün üst üste, 30 gün üst üste, bir günde hedefin iki katı gibi rozetler.
Ayarlar penceresinde bir vitrin.

**Çoklu monitör ve DPI**
Farklı DPI ölçeklerinde ve monitörler arası taşımada widget boyutu/konumu
doğru davranıyor mu? Bug üretmeye çok müsait bir alan, test edilmeli.

**Kısayol tuşu**
Global bir kısayol (ör. `Ctrl+Alt+W`) ile widget'a gitmeden su kaydı.

**Otomatik güncelleme kontrolü**
Açılışta GitHub API'sinden en son sürümü kontrol edip yeni sürüm varsa
ayarlar penceresinde bildir. İndirme işlemini otomatikleştirmeye gerek yok,
sadece haber vermek yeterli.

**Windows dışı platform desteği**
`winotify`, `winsound` ve `GetLastInputInfo` Windows'a özel. Bildirim ve
boşta algılama katmanlarını soyutlayıp Linux/macOS implementasyonları
eklemek, repo'nun erişimini genişletir. Modüler yapı (bölüm 3.1) bunun ön
koşulu.

---

## 6. Önerilen Sıralama

Her satır yaklaşık bir günlük iş.

| # | İş | Etki | Zorluk |
|---|-----|------|--------|
| 1 | About + topics + sosyal önizleme + rozetler | Yüksek | Çok düşük |
| 2 | README: Türkçe karakterler, indirme bölümünü üste alma, SmartScreen açıklaması | Yüksek | Düşük |
| 3 | GIF + masaüstü/ayarlar ekran görüntüleri | Yüksek | Düşük |
| 4 | `README.en.md` | Orta | Düşük |
| 5 | Modüllere ayırma (bölüm 3.1) | Orta | Orta |
| 6 | pytest testleri (bölüm 4) | Orta | Orta |
| 7 | ml bazlı miktar takibi + kap tanımları | Yüksek | Orta |
| 8 | Bildirimden kayıt + geri alma | Yüksek | Orta |
| 9 | Sessiz saatler | Orta | Düşük |
| 10 | Maskot çeşitleri | Orta | Orta |
| 11 | Genişletilmiş istatistikler + dışa aktarma | Orta | Orta |
| 12 | İlk açılış sihirbazı | Orta | Orta |

İlk dört madde toplamda bir güne sığar ve repo'nun dışarıdan görünüşünü en
çok değiştiren kısımdır. 5 ve 6 sonraki her özelliği hızlandıran altyapı
yatırımıdır — özellik eklemeye onlardan sonra geçmek uzun vadede daha
verimli olur.
