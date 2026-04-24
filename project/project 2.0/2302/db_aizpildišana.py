import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "gramatas.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def get_or_create_kategorija(nosaukums):
    cursor.execute("SELECT id FROM kategorijas WHERE nosaukums = ?", (nosaukums,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO kategorijas (nosaukums) VALUES (?)", (nosaukums,))
    return cursor.lastrowid


def get_or_create_autors(vards):
    cursor.execute("SELECT id FROM autori WHERE vards = ?", (vards,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO autori (vards) VALUES (?)", (vards,))
    return cursor.lastrowid


def insert_gramata_if_not_exists(nosaukums, kategorija, cena, autors, attels):
    cursor.execute("SELECT id FROM gramatas WHERE nosaukums = ?", (nosaukums,))
    row = cursor.fetchone()
    kategorija_id = get_or_create_kategorija(kategorija)
    autors_id = get_or_create_autors(autors)
    if row:
        cursor.execute(
            "UPDATE gramatas SET kategorija_id = ?, cena = ?, pieejama = 1, autors_id = ?, attels = ? WHERE id = ?",
            (kategorija_id, cena, autors_id, attels, row[0])
        )
        return
    cursor.execute(
        "INSERT INTO gramatas (nosaukums, kategorija_id, cena, pieejama, autors_id, attels) VALUES (?, ?, ?, 1, ?, ?)",
        (nosaukums, kategorija_id, cena, autors_id, attels)
    )


for kategorija in [
    "Fantastika",
    "Fantāzija",
    "Zinātniskā fantastika",
    "Šausmas",
    "Trilleris",
    "Romāns",
    "Mistika"
]:
    get_or_create_kategorija(kategorija)

for autors in [
    "Sarah J. Maas",
    "Endijs Veijers",
    "Treisija Volfa",
    "Stīvens Kings",
    "Rozamunde Pilčere",
    "Džonatans Strouds",
    "Soman Chainani"
]:
    get_or_create_autors(autors)

gramatas_data = [
    ("Ērkšķu un rožu galms", "Fantāzija", 16.70, "Sarah J. Maas", "erkšķu.jpg"),
    ("Stikla tronis", "Fantāzija", 15.50, "Sarah J. Maas", "stikla_tronis.avif"),
    ("Mersietis", "Zinātniskā fantastika", 14.20, "Endijs Veijers", "marsietis.webp"),
    ("Projekts \"Sveika, Marija\"", "Zinātniskā fantastika", 18.90, "Endijs Veijers", "projects-av-marija.jpg"),
    ("Iekāre", "Fantāzija", 17.30, "Treisija Volfa", "iekare.jpg"),
    ("Mirdzums", "Šausmas", 13.50, "Stīvens Kings", "mirdzums.jpg"),
    ("Zveru kapini", "Trilleris", 12.00, "Stīvens Kings", "zveru-kapini.jpg"),
    ("Tas", "Šausmas", 21.00, "Stīvens Kings", "tas.jpg"),
    ("Gliemežvāku meklētāji", "Romāns", 11.40, "Rozamunde Pilčere", "gliemezvaku.jpg"),
    ("Smaržīgā timiāna meklējumos", "Romāns", 10.80, "Rozamunde Pilčere", "timijana.jpg"),
    ("Amulete no Samarkandas", "Fantāzija", 14.50, "Džonatans Strouds", "amulete.jpg"),
    ("Čukstošais galvaskauss", "Mistika", 13.90, "Džonatans Strouds", "galvaskauss.webp"),
    ("Labā un Ļaunā skola", "Fantāzija", 15.90, "Soman Chainani", "laba_un_launa_skola_1.jpg"),
    ("Pasaule bez prinčiem", "Fantāzija", 16.20, "Soman Chainani", "pasaule-bez-princiem.jpg"),
    ("Pēdējais \"Laimīgi mūžos\"", "Fantāzija", 17.50, "Soman Chainani", "laimigi-muzos.jpg")
]

for gramata in gramatas_data:
    insert_gramata_if_not_exists(*gramata)

cursor.execute("SELECT COUNT(*) FROM klienti")
if cursor.fetchone()[0] == 0:
    cursor.executemany("INSERT INTO klienti (vards, uzvards, personas_kods, telefons) VALUES (?, ?, ?, ?)", [
        ("Anna", "Bērziņa", "010101-12345", "20000001"),
        ("Jānis", "Ozols", "020202-12345", "20000002"),
        ("Laura", "Kalniņa", "030303-12345", "20000003"),
        ("Mārtiņš", "Liepa", "040404-12345", "20000004")
    ])

conn.commit()
conn.close()

print("Datubāze veiksmīgi aizpildīta!")