"""Sistem pakar diagnosis gangguan koneksi internet (Forward Chaining).

Cara menjalankan:
    python sistem_pakar.py
    python sistem_pakar.py kb_internet.json
"""
import json
import sys


def muat_kb(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def syarat_terpenuhi(aturan, memori):
    """mode 'dan': semua syarat ada di memori. mode 'atau': salah satu cukup."""
    ada = [k for k in aturan["jika"] if k in memori]
    if aturan["mode"] == "dan":
        return len(ada) == len(aturan["jika"])
    return len(ada) > 0


def cari_fakta_dasar(kb):
    """Fakta yang tidak pernah menjadi hasil aturan -> ditanyakan ke user."""
    hasil_aturan = {r["maka"] for r in kb["aturan"]}
    urut = []
    for r in kb["aturan"]:
        for k in r["jika"]:
            if k not in hasil_aturan and k not in urut:
                urut.append(k)
    return urut


def tanya_user(kb, fakta_dasar):
    memori = []
    print("Jawab y/t.")
    for i, fakta in enumerate(fakta_dasar, 1):
        teks = kb.get("pertanyaan", {}).get(fakta, f"Apakah {fakta}?")
        while True:
            jawab = input(f"{i}. {teks} (y/t) > ").strip().lower()
            if jawab in ("y", "t"):
                break
            print("   Ketik y atau t saja.")
        if jawab == "y":
            memori.append(fakta)
    return memori


def forward_chaining(kb, fakta_awal):
    """Jalankan aturan yang cocok sampai tidak ada aturan baru."""
    memori = list(fakta_awal)
    asal = {}      # hasil -> aturan penghasilnya (bahan 'alasan')
    siklus = []
    while True:
        cocok = [
            r for r in kb["aturan"]
            if r["maka"] not in memori and syarat_terpenuhi(r, memori)
        ]
        if not cocok:
            break
        r = cocok[0]               # ambil aturan pertama
        memori.append(r["maka"])
        asal[r["maka"]] = r
        siklus.append(r)
    return memori, asal, siklus


def cetak_alasan(fakta, asal, memori, tingkat=1):
    r = asal[fakta]
    syarat = [k for k in r["jika"] if k in memori]
    print(f"{'  ' * tingkat}{fakta}  <- {r['id']} ({', '.join(syarat)})")
    for k in syarat:
        if k in asal:
            cetak_alasan(k, asal, memori, tingkat + 1)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "kb_internet.json"
    kb = muat_kb(path)

    print(kb["judul"])
    fakta_dasar = cari_fakta_dasar(kb)
    fakta_awal = tanya_user(kb, fakta_dasar)

    print()
    print("Fakta awal:", ", ".join(fakta_awal) if fakta_awal else "(tidak ada)")
    print()

    memori, asal, siklus = forward_chaining(kb, fakta_awal)

    for i, r in enumerate(siklus, 1):
        print(f"Siklus {i}: {r['id']} -> {r['maka']}")
    print(f"Siklus {len(siklus) + 1}: tidak ada aturan baru, berhenti")
    print()

    # kesimpulan akhir = hasil aturan yang tidak dipakai sebagai syarat aturan lain
    dipakai_syarat = {k for r in kb["aturan"] for k in r["jika"]}
    kesimpulan = [m for m in asal if m not in dipakai_syarat]

    if kesimpulan:
        print("Kesimpulan:", "; ".join(kesimpulan))
        print("Alasan:")
        for k in kesimpulan:
            cetak_alasan(k, asal, memori)
    else:
        print("Kesimpulan: tidak ada kesimpulan akhir (fakta belum cukup untuk aturan mana pun)")
        if asal:
            print("Informasi sementara:", "; ".join(asal))

    pakai = sorted({r["sumber"] for r in siklus})
    if pakai:
        print()
        print("Sumber yang dipakai:")
        for s in pakai:
            print(f"  {s}: {kb['sumber'][s]}")

    print()
    print("Catatan:", kb["batas"])


if __name__ == "__main__":
    main()
