import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "gramatas.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS kategorijas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS autori (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vards TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS gramatas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums TEXT NOT NULL,
    kategorija_id INTEGER NOT NULL,
    cena REAL NOT NULL,
    pieejama INTEGER NOT NULL DEFAULT 1,
    autors_id INTEGER NOT NULL,
    attels TEXT NOT NULL,
    FOREIGN KEY (kategorija_id) REFERENCES kategorijas(id),
    FOREIGN KEY (autors_id) REFERENCES autori(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS klienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vards TEXT NOT NULL,
    uzvards TEXT NOT NULL,
    personas_kods TEXT NOT NULL,
    telefons TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pasutijumi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klients_id INTEGER NOT NULL,
    cena_kopa REAL NOT NULL,
    preccu_skaits INTEGER NOT NULL,
    laiks TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (klients_id) REFERENCES klienti(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pasutitas_gramatas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pasutijums_id INTEGER NOT NULL,
    gramata_id INTEGER NOT NULL,
    daudzums INTEGER NOT NULL,
    kopa_cena REAL NOT NULL,
    FOREIGN KEY (pasutijums_id) REFERENCES pasutijumi(id),
    FOREIGN KEY (gramata_id) REFERENCES gramatas(id)
)
""")

commands = [
    "ALTER TABLE klienti ADD COLUMN personas_kods TEXT",
    "ALTER TABLE klienti ADD COLUMN telefons TEXT",
    "ALTER TABLE gramatas ADD COLUMN kategorija_id INTEGER",
    "ALTER TABLE gramatas ADD COLUMN cena REAL",
    "ALTER TABLE gramatas ADD COLUMN pieejama INTEGER DEFAULT 1",
    "ALTER TABLE gramatas ADD COLUMN autors_id INTEGER",
    "ALTER TABLE gramatas ADD COLUMN attels TEXT",
    "ALTER TABLE pasutijumi ADD COLUMN cena_kopa REAL",
    "ALTER TABLE pasutijumi ADD COLUMN preccu_skaits INTEGER",
    "ALTER TABLE pasutijumi ADD COLUMN laiks TEXT DEFAULT CURRENT_TIMESTAMP"
]

for command in commands:
    try:
        cursor.execute(command)
    except sqlite3.OperationalError:
        pass

conn.commit()
conn.close()

print("Datubāze izveidota!")