"""
Ajanın kullanacağı simüle araçlar.

Her araç veritabanında çalışır ve yaptığı her işlemi islem_kaydi tablosuna yazar.
Ajan araçları doğrudan değil, calistir() üzerinden çağırır. Böylece güvenlik
katmanı (guard) her çağrıdan önce araya girip işlemi engelleyebilir.

Örnek:
    from veritabani import olustur
    from araclar import calistir

    conn = olustur()
    sonuc = calistir(conn, "email_listele", {})
"""
import json


# ---------------------------------------------------------------- e-posta

def email_listele(conn):
    satirlar = conn.execute("SELECT id, kimden, konu FROM emailler ORDER BY id").fetchall()
    return [dict(s) for s in satirlar]


def email_oku(conn, email_id):
    s = conn.execute("SELECT id, kimden, konu, icerik FROM emailler WHERE id = ?",
                     (email_id,)).fetchone()
    return dict(s) if s else {"hata": f"{email_id} numaralı e-posta bulunamadı"}


def email_gonder(conn, kime, konu, icerik):
    conn.execute("INSERT INTO gonderilen_emailler (kime, konu, icerik) VALUES (?, ?, ?)",
                 (kime, konu, icerik))
    return {"durum": "gönderildi", "kime": kime}


# ---------------------------------------------------------------- dosyalar

def dosya_listele(conn):
    satirlar = conn.execute("SELECT dosya_adi FROM dosyalar WHERE silindi = 0").fetchall()
    return [s["dosya_adi"] for s in satirlar]


def dosya_oku(conn, dosya_adi):
    s = conn.execute("SELECT icerik FROM dosyalar WHERE dosya_adi = ? AND silindi = 0",
                     (dosya_adi,)).fetchone()
    return {"dosya_adi": dosya_adi, "icerik": s["icerik"]} if s else {"hata": "dosya bulunamadı"}


def dosya_sil(conn, dosya_adi):
    n = conn.execute("UPDATE dosyalar SET silindi = 1 WHERE dosya_adi = ? AND silindi = 0",
                     (dosya_adi,)).rowcount
    return {"durum": "silindi" if n else "dosya bulunamadı", "dosya_adi": dosya_adi}


def dosya_paylas(conn, dosya_adi, kime):
    conn.execute("INSERT INTO paylasimlar (dosya_adi, kime) VALUES (?, ?)", (dosya_adi, kime))
    return {"durum": "paylaşıldı", "dosya_adi": dosya_adi, "kime": kime}


# ---------------------------------------------------------------- takvim

def takvime_ekle(conn, baslik, tarih, aciklama=""):
    conn.execute("INSERT INTO takvim (baslik, tarih, aciklama) VALUES (?, ?, ?)",
                 (baslik, tarih, aciklama))
    return {"durum": "eklendi", "baslik": baslik, "tarih": tarih}


ARACLAR = {
    "email_listele": email_listele,
    "email_oku": email_oku,
    "email_gonder": email_gonder,
    "dosya_listele": dosya_listele,
    "dosya_oku": dosya_oku,
    "dosya_sil": dosya_sil,
    "dosya_paylas": dosya_paylas,
    "takvime_ekle": takvime_ekle,
}


# ---------------------------------------------------------------- ortak giriş

def _kaydet(conn, senaryo_id, arac, parametreler, durum, gerekce=None):
    conn.execute(
        "INSERT INTO islem_kaydi (senaryo_id, arac, parametreler, durum, gerekce) "
        "VALUES (?, ?, ?, ?, ?)",
        (senaryo_id, arac, json.dumps(parametreler, ensure_ascii=False), durum, gerekce))
    conn.commit()


def calistir(conn, arac, parametreler, guard=None, kullanici_istegi="", senaryo_id=None):
    """
    Bir aracı çalıştırır ve sonucu döndürür.

    guard verilirse önce ona sorulur. guard şu şekilde bir fonksiyondur:
        guard(arac, parametreler, kullanici_istegi) -> (izin_var_mi: bool, gerekce: str)
    """
    if arac not in ARACLAR:
        return {"hata": f"bilinmeyen araç: {arac}"}

    if guard is not None:
        izin, gerekce = guard(arac, parametreler, kullanici_istegi)
        if not izin:
            _kaydet(conn, senaryo_id, arac, parametreler, "engellendi", gerekce)
            return {"engellendi": True, "gerekce": gerekce}

    try:
        sonuc = ARACLAR[arac](conn, **parametreler)
    except TypeError as e:
        return {"hata": f"hatalı parametre: {e}"}

    _kaydet(conn, senaryo_id, arac, parametreler, "uygulandi")
    return sonuc
