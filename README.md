# PixelDrop

Ekranda yasayan, piksel-art bir su damlasi maskotu ile su icmeyi
hatirlatan hafif bir masaustu araci (TBH: Task Bar Hero mantiginda).

## Ekran Goruntuleri

> Asagidaki goruntuleri gercek uygulamadan alinan ss'lerle
> guncelleyebilirsin: `docs/img/` klasorune koy, asagidaki yollari guncelle.

| Widget (mutlu) | Widget (susamis) | Ayarlar |
|:-:|:-:|:-:|
| *(docs/img/widget_happy.png)* | *(docs/img/widget_thirsty.png)* | *(docs/img/settings.png)* |

## Ozellikler

- **Masaustu widget'i**: Kucuk, cerceve/baslik cubugu olmayan, seffaf
  arka planli, her zaman en ustte duran bir karakter. Zaman gectikce
  maskotun ifadesi degisir: mutlu -> notr -> susamis -> acil (kirmizi,
  yanip soner). Su icince tekrar mutlu olur ve kisa bir "sevinme"
  animasyonu yapar.
- **Surukle-birak**: Karaktere tikla-surukle ile ekranda istedigin yere
  tasi (konum kaydedilir). Tek tiklama (suruklemeden) = "su ictim".
- **Fareyle uzerine gelince** sag ust kosede uc simge belirir: **💤**
  bildirimi 5 dakika erteler, **⚙** kucuk bir ayarlar penceresi acar
  (aralik, boyut, gunluk hedef, duraklat, otomatik duraklama, ses,
  baslangicta calistir - hepsi widget'tan, tepsiye gitmeden), **✕**
  widget'i gizler (tepsi menusunden "Widget'i goster" ile geri
  getirilebilir). Aralarinda yanlislikla birbirine basmayi onlemek icin
  bosluk var; ustelik hangisine daha yakin tiklandiysa o secilir.
- **Kademeli kuruma**: karakterin rengi su icmedikce yavas yavas canli
  mavi-mutludan soluk/kirmizimsi-kurumusa gecer (parlaklik/nem izlenimi
  de azalir), aniden degil surekli/akici bir gecisle.
- **Ilerleme cubugu**: Widget'in altinda, bir sonraki hatirlamaya kalan
  sureyi gosteren kucuk bir cubuk + geri sayim yazisi.
- **Gunluk hedef + seri (streak)**: Widget'te, geri sayimin ustunde
  gunluk kac bardak icildigini gosteren kucuk bardak simgeleri satiri
  (dolu/mavi = icildi, bos/soluk cerceve = kaldi) - hedef 8'den
  buyukse yer kisitindan dolayi "3/10 bardak" seklinde metne doner.
  Hedefe (varsayilan 8 bardak, ayarlardan degistirilebilir) ulasinca
  karakter daha uzun/enerjik bir sekilde "sevinir" ve ayrica bir
  kutlama bildirimi gelir. Gece yarisini gectiginde (uygulama acik
  kalsa bile) sayaç otomatik sifirlanir, onceki gun hedefe ulasildiysa
  seri (kac gun ust uste hedefi tuttugun) bir artar, tutulmadiysa
  sifirlanir. Seri sayisi ayarlar penceresinde gorunur.
- **Bosta/uzaktayken otomatik duraklama**: Klavye/fare 10 dakikadir
  kullanilmadiysa hatirlatici "uzakta" durumuna gecip otomatik
  duraklar (bildirim gelmez); geri donunce sayac sifirlanip normal
  akisina devam eder, boylece bilgisayardan uzaktayken bos yere
  bildirim birikmez. Ayarlardan kapatilabilir.
- **Bildirimden hizli erteleme**: Widget uzerindeki 💤 simgesi ya da
  tepsi menusundeki "5 dk ertele" ile bir sonraki hatirlatmayi 5 dakika
  geciktir.
- **Ayarlarda 7 gunluk mini gecmis**: Ayarlar penceresinde son 7 gunun
  ne kadar su icildigini gosteren kucuk bir cubuk grafik; hedefe
  ulasilan gunler vurgulu renkte gorunur.
- **Dil (Turkce / English)**: Ayarlar penceresinden dil degistirilebilir;
  widget, tepsi menusu, ayarlar penceresi ve bildirim metinleri
  (baslik/icerik) secilen dile gore gosterilir. Varsayilan Turkce.
- **Tepsi (tray) simgesi**: Ayni maskot, kucuk boyutta, sistem
  tepsisinde de durur; sag tikla menuden tum ayarlara erisilir.
- **Aralik**: 15/30/45/60/90/120 dakika arasinda secim.
- **Gunluk hedef**: 4/6/8/10/12/15 bardak arasinda secim.
- **Duraklat/Devam et**, **Bildirim sesi ac/kapa**.
- **Windows baslangicinda calistir**: Acilinca otomatik baslar.
- Native Windows 10/11 toast bildirimi (winotify) ile hatirlatma; ayrica
  sistem sesi (winsound) ile de bir "bip" calar - toast'un kendi sesi
  bazen Windows'un bildirim ayarlari yuzunden (özellikle "Odaklanma
  Yardimcisi"/oyun modu acikken) sessiz kalabildigi icin bu ikinci ses
  yolu daha guvenilir.

## Calistirma (gelistirme)

```
pip install -r requirements.txt
python main.py
```

Konsol penceresi olmadan, arka planda sessizce calistirmak icin:

```
pythonw main.py
```

En kolay yol: `kur_ve_test_et.bat` dosyasina cift tikla — bagimliliklari
kurar, bir test bildirimi gonderir ve uygulamayi baslatir.

## Kullanim

- Ekranda beliren maskota **tek tikla** = su ictim (sayaç sifirlanir,
  gunluk hedefe bir adim daha yaklasilir).
- Maskotu **surukle** = konumunu degistir.
- Maskotun sag ustundeki **💤** = bir sonraki hatirlatmayi 5 dakika
  ertele, **⚙** = ayarlar, **✕** = widget'i gizle (uygulama arka
  planda, tepsi simgesinden calismaya devam eder).
- Tepsi simgesine **sag tikla** = tum ayarlar (aralik, gunluk hedef,
  erteleme, duraklat, otomatik duraklama, widget'i tekrar goster, ses,
  baslangicta calistir, cikis).

Ayarlar (aralik, gunluk hedef, widget konumu/boyutu, gunluk sayac,
seri, gecmis, vb.) `%APPDATA%\PixelDrop\config.json`
dosyasinda saklanir. (Uygulama eskiden "Su Icme Hatirlatici" adiyla
biliniyordu - eski `%APPDATA%\SuIcmeHatirlatici\config.json` varsa
ilk acilista otomatik olarak yeni konuma bir kez kopyalanir, hicbir
veri kaybolmaz.)

## Tek dosya .exe olarak paketleme

`build_exe.bat` dosyasina cift tikla (ya da terminalden calistir).
Cikan dosya: `dist\PixelDrop.exe`

Paketledikten sonra "Windows baslangicinda calistir" secenegini tekrar
ac/kapa ki baslangic kaydi .py yerine .exe'yi gostersin.

## Notlar / mimari

- Arayuz: `tkinter` (stdlib, ekstra kurulum gerekmez) ile seffaf,
  cerçevesiz bir Toplevel penceresi. Karakterin piksel-art gorseli
  calisma zamaninda Pillow ile ciziliyor (harici dosya yok).
- Tepsi simgesi: `pystray`, `run_detached()` ile tkinter'in ana
  dongusunu bloklamadan calisir.
- Zamanlama: ekstra thread/`sleep` dongusu yerine tkinter'in
  `after()` cagrilari kullanilir (saniyede bir durum kontrolu, ~70ms'de
  bir hafif "nefes alma" animasyonu) — boylece boşta CPU kullanimi
  neredeyse sifira yakin kalir.
- Bosta/uzaktayken otomatik duraklama, Windows'un `GetLastInputInfo`
  API'siyle (stdlib `ctypes` uzerinden, ekstra kurulum gerekmez) son
  klavye/fare girdisinden bu yana gecen sureyi olcer; Windows disinda
  ya da API erisilemezse ozellik sessizce devre disi kalir.
- Gunluk hedef/seri ve 7 gunluk gecmis, `config.json` icindeki
  `history` alaninda (tarih -> icilen bardak) son 14 gun saklanarak
  hesaplanir; gun donusu artik sadece baslangicta degil, her saniyelik
  `_tick` kontrolunde de yapilir, boylece uygulama gece boyunca acik
  kalsa da gece yarisinda dogru sifirlanir.
- Diller `STRINGS` sozlugunde (main.py icinde, "tr"/"en") tutulur;
  secim `config.json`'daki `language` alaninda saklanir. Widget/tepsi
  metinleri her yenilendiginde guncel dili okur; ayarlar penceresindeki
  sabit etiketler ise dil degisince pencere yeniden acilarak guncellenir.
