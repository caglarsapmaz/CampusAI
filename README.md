# CampusAI

> **Belgelerini yükle. Soru sor. Cevabını bul.**

Üniversite öğrencilerinin yüklediği akademik PDF belgeleri üzerinden bilgi arayabildiği, doğal dil ile soru sorabildiği belge tabanlı bir akademik asistan. Belgeleriniz işlenir, anlamlı parçalara ayrılır ve sorduğunuz soruya en ilgili içerikler bulunarak yanıtlanır.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
</p>

---

## 📖 Proje Hakkında

**CampusAI**, üniversite öğrencilerinin akademik takvim, ders programı, sınav takvimi, ders içeriği, öğretim üyesi bilgisi ve üniversite duyurusu gibi PDF belgelerini tek bir çalışma alanında toplamasına; bu belgeler arasında manuel arama yapmak yerine doğal dil ile soru sorarak ihtiyaç duyduğu bilgiye hızlıca ulaşmasına olanak tanır.

## ✨ Özellikler

- 📄 **PDF belge yükleme** — akademik takvim, ders programı, sınav takvimi ve benzeri belgeleri işleme
- ✂️ **Akıllı metin parçalama** — çıkarılan uzun metinleri anlamlı chunk'lara ayırma
- 🔍 **İlgili içerik bulma (retrieval)** — sorulan soruyla en alakalı belge parçalarını getirme
- 💬 **Doğal dil ile soru-cevap** — belgeler arasında elle arama yapmaya gerek kalmadan sohbet arayüzü üzerinden yanıt alma
- 🗂️ **Sohbet geçmişi ve yeni sohbet** — çalışma alanları arasında geçiş
- 🗃️ **Yerel SQLite veritabanı** — kalıcı verilerin `campus.db` üzerinde saklanması
- 🖥️ **Dark tema, responsive arayüz** — sidebar, chat alanı ve kaynak/belge sonuçları ile CampusAI branding'i
- 🧩 **Modüler mimari** — PDF okuma, parçalama, retrieval, veritabanı ve UI stilleri ayrı modüllerde

## Tech Stack

- Python
- Streamlit
- PyMuPDF (fitz)
- Requests
- SQLite
- Microsoft Foundry Local
- Phi-4-mini

## 🛠️ Kullanılan Teknolojiler

| Katman | Tercih |
|---|---|
| Dil | Python |
| Veritabanı | SQLite (`campus.db`) |
| Belge işleme | `pdf_reader.py` — PDF metin çıkarma |
| Metin parçalama | `chunker.py` — chunk tabanlı bölme |
| Bilgi getirme | `retrieval.py` — soruya göre en ilgili içerik bulma |
| Arayüz stilleri | `styles.py` — renkler, kartlar, sidebar, chat alanı |

## 🗂️ Proje Yapısı

```
CampusAIV3/
├── app.py
├── database/
│   └── campus.db
├── README.md
├── requirements.txt
└── src/
    ├── __init__.py
    ├── chunker.py
    ├── database.py
    ├── pdf_reader.py
    ├── retrieval.py
    └── styles.py
```

## 🧩 Dosya ve Klasörlerin Görevleri

| Dosya / Klasör | Görev |
|---|---|
| `app.py` | Ana giriş noktası — uygulamayı başlatır, belge yükleme ve soru-cevap akışını yönetir, `src/` modüllerini bir araya getirir |
| `database/campus.db` | CampusAI'nin kullandığı SQLite veritabanı (elle değiştirilmemeli, `src/database.py` üzerinden yönetilmeli) |
| `src/pdf_reader.py` | PDF dosyasını açma, sayfalardaki metni okuma ve uygulamanın kullanabileceği forma dönüştürme |
| `src/chunker.py` | Uzun metinleri retrieval için anlamlı küçük parçalara ayırma |
| `src/retrieval.py` | Kullanıcı sorusuyla ilgili belge içeriklerini bulma |
| `src/database.py` | Veritabanı bağlantısı, ekleme, okuma, güncelleme ve sorguları merkezi olarak yönetme |
| `src/styles.py` | Renkler, butonlar, kartlar, input alanları, sidebar, chat alanı gibi UI bileşenlerinin stilleri |

## 🔄 Uygulamanın Genel Çalışma Akışı

```text
                    ┌──────────────┐
                    │    Kullanıcı │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    app.py    │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌──────────────┐          ┌──────────────┐
       │ PDF yükleme  │          │ Soru sorma   │
       └──────┬───────┘          └──────┬───────┘
              │                         │
              ▼                         ▼
       ┌──────────────┐          ┌──────────────┐
       │ pdf_reader   │          │  retrieval   │
       └──────┬───────┘          └──────┬───────┘
              │                         │
              ▼                         │
       ┌──────────────┐                 │
       │   chunker    │                 │
       └──────┬───────┘                 │
              │                         │
              └────────────┬────────────┘
                           ▼
                    ┌──────────────┐
                    │  database.py │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   campus.db  │
                    └──────────────┘
```

## 🚀 Kurulum

```bash
# Proje klasörüne gir
cd CampusAIV3

# Sanal ortam oluştur (macOS / Linux)
python3 -m venv venv
source venv/bin/activate

# Sanal ortam oluştur (Windows)
python -m venv venv
venv\Scriptsctivate

# Gerekli paketleri yükle
pip install -r requirements.txt
```

## ▶️ Uygulamayı Çalıştırma

```bash
streamlit run app.py
```

Uygulama başlatıldıktan sonra terminalde gösterilen yerel adres üzerinden web arayüzüne erişilebilir.

## 📄 Belge İşleme

CampusAI'nin temel kullanım senaryosu akademik PDF belgeleri üzerinden çalışmaktır. Örnek belgeler:

- Akademik takvimler
- Ders programları
- Sınav takvimleri
- Ders içerikleri
- Öğretim üyesi bilgileri
- Üniversite duyuruları

Temel belge işleme zinciri:

```text
PDF → pdf_reader.py → Metin → chunker.py → Parçalara ayrılmış içerik
    → Veritabanı / retrieval → Kullanıcı sorgusu → İlgili belge içeriği
```

## 🖥️ Kullanıcı Arayüzü

Ana UI bileşenleri: sidebar, yeni sohbet, sohbet geçmişi, belge yükleme alanı, yüklü belgeler, çalışma alanı bilgileri, chat alanı, soru giriş alanı, kaynak/belge sonuçları, responsive düzen, dark tema ve CampusAI branding. Arayüz ile ilgili stiller `src/styles.py` içerisinde tutulur.

## 🔐 Veri ve Gizlilik

Yüklenen akademik belgeler uygulamanın veri işleme sürecinin bir parçasıdır. Projeyi gerçek kullanıcılarla kullanıma açmadan önce şu konular ayrıca değerlendirilmelidir:

- Yüklenen dosyaların güvenliği
- Dosya boyutu ve dosya türü kontrolleri
- Kullanıcı verilerinin korunması
- Veritabanı erişim güvenliği
- Hatalı veya zararlı dosyaların engellenmesi
- Üretim ortamında secret / API key yönetimi
- Loglarda hassas bilgi tutulmaması

## 📌 Geliştirme Notları

1. PDF işleme kodlarını `pdf_reader.py` içerisinde tut.
2. Metin parçalama işlemlerini `chunker.py` içerisinde tut.
3. Retrieval mantığını `retrieval.py` içerisinde tut.
4. Veritabanı sorgularını `database.py` üzerinden yönet.
5. UI/stil değişikliklerini `styles.py` içerisinde tut.
6. `app.py` dosyasını mümkün olduğunca ana orkestrasyon katmanı olarak kullan.
7. Yeni özellik eklerken mevcut çalışan belge işleme ve retrieval akışını bozmamaya dikkat et.
8. Veritabanı dosyasını doğrudan değiştirmek yerine kontrollü migration / initialization yaklaşımı kullan.

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen bir issue açın veya pull request gönderin.

1. Bu depoyu fork'layın
2. Yeni bir branch oluşturun (`git checkout -b ozellik/yeni-ozellik`)
3. Değişikliklerinizi commit'leyin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push'layın (`git push origin ozellik/yeni-ozellik`)
5. Bir Pull Request açın

## 🎯 Projenin Amacı

CampusAI'nin amacı, üniversite öğrencilerinin farklı akademik belgeler arasında manuel olarak arama yapmak yerine belgelerini tek bir çalışma alanında yönetebilmesini ve doğal dil ile soru sorarak ihtiyaç duyduğu akademik bilgiye hızlıca ulaşabilmesini sağlamaktır.

> **CampusAI — Üniversite belgelerinizi anlayan akademik asistan.**

---

<p align="center">Made with ❤️ by <a href="https://www.linkedin.com/in/caglarsapmaz/">caglarsapmaz</a></p>
