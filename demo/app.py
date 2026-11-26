import streamlit as st

epostalar = [
    {"konu": "Toplantı hatırlatması", "gonderen": "ali@sirket.com",
     "icerik": "Yarın saat 10:00'da toplantımız var."},
    {"konu": "Kargonuz yolda", "gonderen": "kargo@firma.com",
     "icerik": "Siparişiniz yarın teslim edilecek."},
    {"konu": "Fatura bilgisi", "gonderen": "fatura@banka.com",
     "icerik": "Bu ayki faturanız hazır."},
    {"konu": "Ders programı", "gonderen": "ogrenci@okul.edu",
     "icerik": "Yeni dönem ders programı yayınlandı."},
    {"konu": "Proje toplantısı", "gonderen": "cansu@okul.edu",
     "icerik": "Perşembe günü grup toplantısı yapacağız."},
    {"konu": "Randevu onayı", "gonderen": "klinik@saglik.com",
     "icerik": "Cuma günü saat 14:00 randevunuz onaylandı."},
    {"konu": "Kütüphane hatırlatması", "gonderen": "kutuphane@okul.edu",
     "icerik": "Ödünç aldığınız kitabın iade tarihi yaklaşıyor."},
    {"konu": "Sipariş özeti", "gonderen": "siparis@magaza.com",
     "icerik": "2 ürünlük siparişiniz hazırlanıyor."},
    {"konu": "Etkinlik daveti", "gonderen": "kulup@okul.edu",
     "icerik": "Cumartesi günkü kariyer günümüze davetlisiniz."},
    {"konu": "Haftalık özet", "gonderen": "bilgi@haber.com",
     "icerik": "Bu haftanın öne çıkan haberleri hazır."},
]

def eposta_goster(e):
    with st.expander(e["konu"]):
        st.write("Gönderen:", e["gonderen"])
        st.write(e["icerik"])


st.title("Gelen Kutusu")

arama = st.text_input("Konuda ara")
sadece_okul = st.toggle("Sadece okul e-postaları")

gosterilecek = []
for e in epostalar:
    if arama.lower() not in e["konu"].lower():
        continue
    if sadece_okul and "okul.edu" not in e["gonderen"]:
        continue
    gosterilecek.append(e)

sol, sag = st.columns(2)
sol.metric("Toplam e-posta", len(epostalar))
sag.metric("Gösterilen", len(gosterilecek))

if st.button("Özet göster"):
    st.success(f"{len(gosterilecek)} e-posta gösteriliyor.")

for e in gosterilecek:
    eposta_goster(e)