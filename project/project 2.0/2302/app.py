from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3
import os
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gramatas.db")
IMAGES_DIR = os.path.join(BASE_DIR, "images")

app = Flask(__name__)
app.secret_key = "supersecretkey"


def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def initialize_db():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    conn = get_db_connection()
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
    conn.commit()
    conn.close()


def migrate_klienti():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(klienti)")
    cols = [row[1] for row in cursor.fetchall()]
    if "gramata_id" in cols:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS klienti_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vards TEXT NOT NULL,
                uzvards TEXT NOT NULL,
                personas_kods TEXT NOT NULL,
                telefons TEXT NOT NULL
            )
        """)
        cursor.execute("""
            INSERT INTO klienti_new (id, vards, uzvards, personas_kods, telefons)
            SELECT id, vards, uzvards, personas_kods, telefons FROM klienti
        """)
        cursor.execute("DROP TABLE klienti")
        cursor.execute("ALTER TABLE klienti_new RENAME TO klienti")
    conn.commit()
    conn.close()


def safe_alter():
    conn = get_db_connection()
    cursor = conn.cursor()
    commands = [
        "ALTER TABLE gramatas ADD COLUMN kategorija_id INTEGER",
        "ALTER TABLE gramatas ADD COLUMN cena REAL",
        "ALTER TABLE gramatas ADD COLUMN pieejama INTEGER DEFAULT 1",
        "ALTER TABLE gramatas ADD COLUMN autors_id INTEGER",
        "ALTER TABLE gramatas ADD COLUMN attels TEXT",
        "ALTER TABLE klienti ADD COLUMN personas_kods TEXT",
        "ALTER TABLE klienti ADD COLUMN telefons TEXT",
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


initialize_db()
safe_alter()
migrate_klienti()


def get_gramatas(autors_id=None, kategorija_id=None, max_cena=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT gramatas.id, gramatas.nosaukums, kategorijas.nosaukums, gramatas.cena, gramatas.pieejama, autori.vards, gramatas.attels
        FROM gramatas
        LEFT JOIN kategorijas ON gramatas.kategorija_id = kategorijas.id
        LEFT JOIN autori ON gramatas.autors_id = autori.id
        WHERE 1=1
    """
    params = []
    if autors_id:
        query += " AND gramatas.autors_id = ?"
        params.append(autors_id)
    if kategorija_id:
        query += " AND gramatas.kategorija_id = ?"
        params.append(kategorija_id)
    if max_cena:
        query += " AND gramatas.cena <= ?"
        params.append(float(max_cena))
    query += " ORDER BY gramatas.id DESC"
    cursor.execute(query, params)
    data = [{
        "id": row[0],
        "nosaukums": row[1],
        "kategorija": row[2],
        "cena": row[3],
        "pieejama": row[4],
        "autors": row[5],
        "attels": row[6]
    } for row in cursor.fetchall()]
    conn.close()
    return data


def get_kategorijas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nosaukums FROM kategorijas ORDER BY nosaukums")
    data = [{"id": row[0], "nosaukums": row[1]} for row in cursor.fetchall()]
    conn.close()
    return data


def get_autori():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, vards FROM autori ORDER BY vards")
    data = [{"id": row[0], "vards": row[1]} for row in cursor.fetchall()]
    conn.close()
    return data


def get_klienti():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, vards, uzvards, personas_kods, telefons FROM klienti ORDER BY uzvards, vards")
    data = [{"id": row[0], "vards": row[1], "uzvards": row[2], "personas_kods": row[3], "telefons": row[4]} for row in cursor.fetchall()]
    conn.close()
    return data


def get_pasutijumi():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            pasutijumi.id,
            pasutijumi.laiks,
            klienti.vards,
            klienti.uzvards,
            pasutijumi.cena_kopa,
            pasutijumi.preccu_skaits,
            GROUP_CONCAT(gramatas.nosaukums || ' x' || pasutitas_gramatas.daudzums, ', ')
        FROM pasutijumi
        LEFT JOIN klienti ON pasutijumi.klients_id = klienti.id
        LEFT JOIN pasutitas_gramatas ON pasutitas_gramatas.pasutijums_id = pasutijumi.id
        LEFT JOIN gramatas ON gramatas.id = pasutitas_gramatas.gramata_id
        GROUP BY pasutijumi.id, pasutijumi.laiks, klienti.vards, klienti.uzvards, pasutijumi.cena_kopa, pasutijumi.preccu_skaits
        ORDER BY pasutijumi.id DESC
    """)
    data = [{
        "id": row[0],
        "laiks": row[1],
        "vards": row[2],
        "uzvards": row[3],
        "cena_kopa": row[4],
        "preccu_skaits": row[5],
        "elementi": row[6] or ""
    } for row in cursor.fetchall()]
    conn.close()
    return data


def save_image(file):
    if not file or not file.filename:
        return None
    ext = os.path.splitext(file.filename)[1]
    name = f"{uuid.uuid4().hex}{ext}"
    file.save(os.path.join(IMAGES_DIR, name))
    return name


@app.route("/")
def index():
    return redirect(url_for("gramatas"))


@app.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(IMAGES_DIR, filename)


@app.route("/gramatas")
def gramatas():
    autors_id = request.args.get("autors_id", "").strip()
    kategorija_id = request.args.get("kategorija_id", "").strip()
    max_cena = request.args.get("max_cena", "").strip()
    return render_template(
        "gramatas.html",
        gramatas=get_gramatas(autors_id or None, kategorija_id or None, max_cena or None),
        autori=get_autori(),
        kategorijas=get_kategorijas(),
        selected_autors=autors_id,
        selected_kategorija=kategorija_id,
        selected_cena=max_cena
    )


@app.route("/pievienot_gramatu", methods=["GET", "POST"])
def pievienot_gramatu():
    if request.method == "POST":
        nosaukums = request.form.get("nosaukums", "").strip()
        kategorija_id = request.form.get("kategorija_id")
        cena = request.form.get("cena", "").strip()
        pieejama = request.form.get("pieejama")
        autors_id = request.form.get("autors_id")
        attels = request.files.get("attels")
        if not nosaukums or not kategorija_id or not cena or pieejama is None or not autors_id or not attels or not attels.filename:
            flash("Visi lauki ir obligāti jāaizpilda!", "error")
            return redirect(url_for("pievienot_gramatu"))
        image_name = save_image(attels)
        if not image_name:
            flash("Kļūda augšupielādējot attēlu!", "error")
            return redirect(url_for("pievienot_gramatu"))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO gramatas (nosaukums, kategorija_id, cena, pieejama, autors_id, attels) VALUES (?, ?, ?, ?, ?, ?)",
            (nosaukums, kategorija_id, float(cena), int(pieejama), autors_id, image_name)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("gramatas"))
    return render_template("pievienot_gramatu.html", kategorijas=get_kategorijas(), autori=get_autori())


@app.route("/dzest_gramatu", methods=["GET", "POST"])
def dzest_gramatu():
    if request.method == "POST":
        gramata_id = request.form.get("gramata_id")
        if gramata_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pasutitas_gramatas WHERE gramata_id = ?", (gramata_id,))
            cursor.execute("DELETE FROM gramatas WHERE id = ?", (gramata_id,))
            conn.commit()
            conn.close()
        return redirect(url_for("dzest_gramatu"))
    return render_template("dzest_gramatu.html", gramatas=get_gramatas())


@app.route("/pievienot_klientu", methods=["GET", "POST"])
def pievienot_klientu():
    if request.method == "POST":
        vards = request.form.get("vards", "").strip()
        uzvards = request.form.get("uzvards", "").strip()
        personas_kods = request.form.get("personas_kods", "").strip()
        telefons = request.form.get("telefons", "").strip()
        if not vards or not uzvards or not personas_kods or not telefons:
            flash("Visi lauki ir obligāti jāaizpilda!", "error")
            return redirect(url_for("pievienot_klientu"))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO klienti (vards, uzvards, personas_kods, telefons) VALUES (?, ?, ?, ?)",
            (vards, uzvards, personas_kods, telefons)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("pievienot_klientu"))
    return render_template("pievienot_klientu.html")


@app.route("/dzest_klientu", methods=["GET", "POST"])
def dzest_klientu():
    if request.method == "POST":
        klients_id = request.form.get("klients_id")
        if klients_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pasutijumi WHERE klients_id = ?", (klients_id,))
            cursor.execute("DELETE FROM klienti WHERE id = ?", (klients_id,))
            conn.commit()
            conn.close()
        return redirect(url_for("dzest_klientu"))
    return render_template("dzest_klientu.html", klienti=get_klienti())


@app.route("/rediget_klientu", methods=["GET"])
def rediget_klientu():
    klients_id = request.args.get("klients_id")
    klienti = get_klienti()
    klients = None
    if klients_id:
        for item in klienti:
            if str(item["id"]) == str(klients_id):
                klients = item
                break
    return render_template("rediget_klientu.html", klienti=klienti, klients=klients)


@app.route("/saglabat_klientu", methods=["POST"])
def saglabat_klientu():
    klients_id = request.form.get("klients_id")
    vards = request.form.get("vards")
    uzvards = request.form.get("uzvards")
    personas_kods = request.form.get("personas_kods")
    telefons = request.form.get("telefons")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE klienti SET vards = ?, uzvards = ?, personas_kods = ?, telefons = ? WHERE id = ?",
        (vards, uzvards, personas_kods, telefons, klients_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("rediget_klientu", klients_id=klients_id))


@app.route("/kategorijas")
def kategorijas():
    return render_template("kategorijas.html", kategorijas=get_kategorijas())


@app.route("/klienti")
def klienti():
    return render_template("klienti.html", klienti=get_klienti())


@app.route("/pasutijumi")
def pasutijumi():
    return render_template("pasutijumi.html", pasutijumi=get_pasutijumi())


@app.route("/pievienot_kategoriju", methods=["GET", "POST"])
def pievienot_kategoriju():
    if request.method == "POST":
        nosaukums = request.form.get("nosaukums", "").strip()
        if not nosaukums:
            flash("Nosaukums ir obligāts!", "error")
            return redirect(url_for("pievienot_kategoriju"))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO kategorijas (nosaukums) VALUES (?)", (nosaukums,))
        conn.commit()
        conn.close()
        return redirect(url_for("kategorijas"))
    return render_template("pievienot_kategoriju.html")


@app.route("/pievienot_autoru", methods=["GET", "POST"])
def pievienot_autoru():
    if request.method == "POST":
        vards = request.form.get("vards", "").strip()
        if not vards:
            flash("Autora vārds ir obligāts!", "error")
            return redirect(url_for("pievienot_autoru"))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO autori (vards) VALUES (?)", (vards,))
        conn.commit()
        conn.close()
        return redirect(url_for("gramatas"))
    return render_template("pievienot_autoru.html")


@app.route("/dzest_autoru", methods=["GET", "POST"])
def dzest_autoru():
    if request.method == "POST":
        autors_id = request.form.get("autors_id")
        if autors_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM autori WHERE id = ?", (autors_id,))
            conn.commit()
            conn.close()
        return redirect(url_for("dzest_autoru"))
    return render_template("dzest_autoru.html", autori=get_autori())


@app.route("/dzest_kategoriju", methods=["GET", "POST"])
def dzest_kategoriju():
    if request.method == "POST":
        kategorija_id = request.form.get("kategorija_id")
        if kategorija_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kategorijas WHERE id = ?", (kategorija_id,))
            conn.commit()
            conn.close()
        return redirect(url_for("dzest_kategoriju"))
    return render_template("dzest_kategoriju.html", kategorijas=get_kategorijas())


@app.route("/pievienot_pasutijumu", methods=["GET", "POST"])
def pievienot_pasutijumu():
    if request.method == "POST":
        klients_id = request.form.get("klients_id")
        gramatu_ids = request.form.getlist("gramata_id")
        daudzumi = request.form.getlist("daudzums")
        if not klients_id or not gramatu_ids:
            flash("Aizpildiet klientu un izvēlieties vismaz vienu grāmatu!", "error")
            return redirect(url_for("pievienot_pasutijumu"))
        rows = []
        for gid, d in zip(gramatu_ids, daudzumi):
            if gid and d and int(d) > 0:
                rows.append((int(gid), int(d)))
        if not rows:
            flash("Pasūtījumā nav derīgu grāmatu!", "error")
            return redirect(url_for("pievienot_pasutijumu"))
        conn = get_db_connection()
        cursor = conn.cursor()
        total_price = 0.0
        total_qty = 0
        line_items = []
        for gid, qty in rows:
            cursor.execute("SELECT cena FROM gramatas WHERE id = ?", (gid,))
            row = cursor.fetchone()
            if row:
                line_total = float(row[0]) * qty
                total_price += line_total
                total_qty += qty
                line_items.append((gid, qty, line_total))
        if not line_items:
            conn.close()
            flash("Grāmatas netika atrastas!", "error")
            return redirect(url_for("pievienot_pasutijumu"))
        cursor.execute(
            "INSERT INTO pasutijumi (klients_id, cena_kopa, preccu_skaits, laiks) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (klients_id, total_price, total_qty)
        )
        pasutijums_id = cursor.lastrowid
        for gid, qty, line_total in line_items:
            cursor.execute(
                "INSERT INTO pasutitas_gramatas (pasutijums_id, gramata_id, daudzums, kopa_cena) VALUES (?, ?, ?, ?)",
                (pasutijums_id, gid, qty, line_total)
            )
        conn.commit()
        conn.close()
        flash("Pasūtījums pievienots!", "success")
        return redirect(url_for("pievienot_pasutijumu"))
    return render_template("pievienot_pasutijumu.html", klienti=get_klienti(), gramatas=get_gramatas())


if __name__ == "__main__":
    app.run(debug=True)