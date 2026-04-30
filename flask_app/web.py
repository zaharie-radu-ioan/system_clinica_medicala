import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from app.db import run_select, run_execute

app = Flask(__name__)
app.secret_key = "dev-secret"


CRUD_CONFIG = {
    "utilizator": {
        "pk": "id_utilizator",
        "title": "Utilizatori",
        "create_fields": ["username", "parola", "email", "rol"],
        "update_fields": ["parola", "email", "rol"],
        "list_fields": ["id_utilizator", "username", "parola","email", "rol"],
        "default_sort": "id_utilizator ASC",
        "choices": {"rol": ["admin", "medic", "pacient"]},
        "children": [
            {"table": "medic",    "fk": "id_utilizator"},
            {"table": "pacient",  "fk": "id_utilizator"},
            {"table": "user_log", "fk": "id_utilizator"},
            {"table": "notificare", "fk": "id_utilizator"},
        ]
    },
    "medic": {
        "pk": "id_medic",
        "title": "Medici",
        "create_fields": ["id_utilizator", "nume_medic", "cod_parafa", "specializare", "program"],
        "update_fields": ["nume_medic", "specializare", "program"],
        "list_fields": ["id_medic", "nume_medic", "cod_parafa", "specializare", "program"],
        "default_sort": "id_medic ASC",
        "fk_dropdowns": {"id_utilizator": ("utilizator", "id_utilizator", "username")},
        "children": [{"table": "programare", "fk": "id_medic"}]
    },
    "pacient": {
        "pk": "id_pacient",
        "title": "Pacienți",
        "create_fields": ["id_utilizator", "nume", "prenume", "CNP", "data_nasterii", "sex", "telefon"],
        "update_fields": ["telefon", "nume", "prenume"],
        "list_fields": ["id_pacient", "nume", "prenume", "CNP", "telefon"],
        "default_sort": "id_pacient ASC",
        "fk_dropdowns": {"id_utilizator": ("utilizator", "id_utilizator", "username")},
        "children": [
            {"table": "programare",    "fk": "id_pacient"},
            {"table": "dosar_medical", "fk": "id_pacient"},
        ]
    },
    "dosar_medical": {
        "pk": "id_dosar",
        "title": "Dosare Medicale",
        "create_fields": ["id_pacient", "grupa_sanguina", "rh", "alergii", "boli_cronice", "observatii"],
        "update_fields": ["grupa_sanguina", "rh", "alergii", "boli_cronice", "observatii"],
        "list_fields": ["id_dosar", "id_pacient", "grupa_sanguina", "rh", "alergii", "boli_cronice"],
        "default_sort": "id_dosar ASC",
        "choices": {
            "grupa_sanguina": ["A1", "A2", "B", "AB", "O"],
            "rh": ["+", "-"],
        },
        "fk_dropdowns": {"id_pacient": ("pacient", "id_pacient", "nume")},
    },
    "programare": {
        "pk": "id_programare",
        "title": "Programări",
        "create_fields": ["data", "ora", "cabinet", "id_pacient", "id_medic", "id_utilizator", "status"],
        "update_fields": ["data", "ora", "status", "cabinet"],
        "list_fields": ["id_programare", "data", "ora", "cabinet", "id_pacient", "id_medic", "status"],
        "default_sort": "id_programare DESC",
        "choices": {"status": ["programata", "finalizata", "anulata"]},
        "fk_dropdowns": {
            "id_pacient":    ("pacient",    "id_pacient",    "nume"),
            "id_medic":      ("medic",      "id_medic",      "nume_medic"),
            "id_utilizator": ("utilizator", "id_utilizator", "username"),
        },
        "children": [{"table": "consultatie", "fk": "id_programare"}]
    },
    "consultatie": {
        "pk": "id_consultatie",
        "title": "Consultații",
        "create_fields": ["id_programare", "diagnostic", "analize_recomandate", "recomandari_tratament", "cost"],
        "update_fields": ["diagnostic", "analize_recomandate", "recomandari_tratament", "cost"],
        "list_fields": ["id_consultatie", "id_programare", "diagnostic", "analize_recomandate", "recomandari_tratament", "cost"],
        "default_sort": "id_consultatie ASC",
        "fk_dropdowns": {"id_programare": ("programare", "id_programare", "data")},
        "children": [
            {"table": "factura", "fk": "id_consultatie"},
            {"table": "reteta",  "fk": "id_consultatie"},
        ]
    },
    "servicii_medicale": {
        "pk": "id_serviciu",
        "title": "Servicii Medicale",
        "create_fields": ["cod_serviciu", "denumire", "pret"],
        "update_fields": ["cod_serviciu", "denumire", "pret"],
        "list_fields": ["id_serviciu", "cod_serviciu", "denumire", "pret"],
        "default_sort": "id_serviciu ASC",
        "children": [{"table": "factura", "fk": "id_serviciu"}]
    },
    "factura": {
        "pk": "id_linie",
        "title": "Linii Factură",
        "create_fields": ["id_consultatie", "id_serviciu", "cantitate", "pret_unitar"],
        "update_fields": ["cantitate", "pret_unitar"],
        "list_fields": ["id_linie", "id_consultatie", "id_serviciu", "cantitate", "pret_unitar"],
        "default_sort": "id_linie ASC",
        "fk_dropdowns": {
            "id_consultatie": ("consultatie",      "id_consultatie", "diagnostic"),
            "id_serviciu":    ("servicii_medicale", "id_serviciu",    "denumire"),
        }
    },
    "medicament": {
        "pk": "id_medicament",
        "title": "Medicamente",
        "create_fields": ["denumire", "forma", "prospect"],
        "update_fields": ["denumire", "forma", "prospect"],
        "list_fields": ["id_medicament", "denumire", "forma"],
        "default_sort": "id_medicament ASC",
        "children": [{"table": "reteta_medicament", "fk": "id_medicament"}]
    },
    "reteta": {
        "pk": "id_reteta",
        "title": "Rețete",
        "create_fields": ["id_consultatie", "data_emiterii", "valabila_pana"],
        "update_fields": ["valabila_pana"],
        "list_fields": ["id_reteta", "id_consultatie", "data_emiterii", "valabila_pana"],
        "default_sort": "id_reteta DESC",
        "fk_dropdowns": {"id_consultatie": ("consultatie", "id_consultatie", "diagnostic")},
        "children": [{"table": "reteta_medicament", "fk": "id_reteta"}]
    },
    "reteta_medicament": {
        "pk": "id",
        "title": "Linii Rețetă",
        "create_fields": ["id_reteta", "id_medicament", "doza", "frecventa", "durata"],
        "update_fields": ["doza", "frecventa", "durata"],
        "list_fields": ["id", "id_reteta", "id_medicament", "doza", "frecventa", "durata"],
        "default_sort": "id ASC",
        "fk_dropdowns": {
            "id_reteta":     ("reteta",      "id_reteta",     "data_emiterii"),
            "id_medicament": ("medicament",  "id_medicament", "denumire"),
        }
    },
    "notificare": {
        "pk": "id_notificare",
        "title": "Notificări",
        "create_fields": ["id_utilizator", "mesaj", "tip", "citita"],
        "update_fields": ["citita"],
        "list_fields": ["id_notificare", "id_utilizator", "mesaj", "tip", "citita", "created_at"],
        "default_sort": "id_notificare DESC",
        "choices": {
            "tip":    ["reminder", "anulare", "confirmare", "sistem"],
            "citita": ["0", "1"],
        },
        "fk_dropdowns": {"id_utilizator": ("utilizator", "id_utilizator", "username")},
    },
    "user_log": {
        "pk": "id_log",
        "title": "Istoric Acțiuni",
        "create_fields": ["id_utilizator", "actiune", "ip_address"],
        "update_fields": [],
        "list_fields": ["id_log", "id_utilizator", "actiune", "created_at"],
        "default_sort": "id_log DESC",
        "fk_dropdowns": {"id_utilizator": ("utilizator", "id_utilizator", "username")}
    },
}


def ensure_table_allowed(table):
    if table not in CRUD_CONFIG:
        abort(404)
    return CRUD_CONFIG[table]


def has_any_user():
    try:
        rows = run_select("SELECT id_utilizator FROM utilizator LIMIT 1;")
        return bool(rows)
    except Exception:
        return False


def record_exists(table, field, value):
    ensure_table_allowed(table)
    q = f"SELECT 1 FROM {table} WHERE {field}=%s LIMIT 1;"
    return bool(run_select(q, (value,)))


def fetch_list(table):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]
    if cols[0] != pk:
        cols = [pk] + [c for c in cols if c != pk]
    q = f"SELECT {', '.join(cols)} FROM {table} ORDER BY {cfg.get('default_sort', pk+' DESC')};"
    rows = run_select(q)
    return cols, rows


def fetch_by_id(table, rec_id):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]
    if cols[0] != pk:
        cols = [pk] + [c for c in cols if c != pk]
    q = f"SELECT {', '.join(cols)} FROM {table} WHERE {pk}=%s LIMIT 1;"
    rows = run_select(q, (rec_id,))
    return cols, (rows[0] if rows else None)


def build_fk_options(cfg):
    options = {}
    for field, spec in cfg.get("fk_dropdowns", {}).items():
        parent_table, parent_pk, label_col = spec
        rows = run_select(
            f"SELECT {parent_pk}, {label_col} FROM {parent_table} ORDER BY {parent_pk} DESC;"
        )
        options[field] = [(str(r[0]), str(r[1])) for r in rows]
    return options


def insert_record(table, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["create_fields"]

    values = []
    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Camp obligatoriu lipsa: {f}")
        values.append(v)

    for f, v in zip(fields, values):
        if "fk_dropdowns" in cfg and f in cfg["fk_dropdowns"]:
            parent_table, parent_pk, _label = cfg["fk_dropdowns"][f]
            if not record_exists(parent_table, parent_pk, v):
                raise ValueError(f"Valoare invalida pentru {f} (nu exista in {parent_table}).")

    cols = ", ".join(fields)
    placeholders = ", ".join(["%s"] * len(fields))
    q = f"INSERT INTO {table} ({cols}) VALUES ({placeholders});"
    run_execute(q, tuple(values))


def update_record(table, rec_id, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["update_fields"]
    if not fields:
        raise ValueError("Acest tabel nu are UPDATE in template.")

    pairs = []
    values = []
    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Camp obligatoriu lipsa: {f}")
        pairs.append(f"{f}=%s")
        values.append(v)

    values.append(rec_id)
    q = f"UPDATE {table} SET {', '.join(pairs)} WHERE {cfg['pk']}=%s;"
    run_execute(q, tuple(values))


def delete_record_safe(table, rec_id):
    cfg = ensure_table_allowed(table)

    for ch in cfg.get("children", []):
        run_execute(f"DELETE FROM {ch['table']} WHERE {ch['fk']}=%s;", (rec_id,))

    run_execute(f"DELETE FROM {table} WHERE {cfg['pk']}=%s;", (rec_id,))


@app.before_request
def guard_if_no_users():
    allowed = {"/", "/setup", "/seed-admin", "/search"}
    if request.path.startswith("/static/"):
        return
    if not has_any_user() and request.path not in allowed:
        return redirect(url_for("setup_required"))


@app.route("/")
def index():
    counts = {}
    ready = has_any_user()
    for t in CRUD_CONFIG.keys():
        try:
            counts[t] = run_select(f"SELECT COUNT(*) FROM {t};")[0][0] if ready else 0
        except Exception:
            counts[t] = 0
    return render_template("index.html", site_cfg=CRUD_CONFIG, counts=counts, ready=ready)


@app.route("/setup")
def setup_required():
    return render_template("setup_required.html", site_cfg=CRUD_CONFIG)


@app.route("/seed-admin")
def seed_admin():
    if has_any_user():
        flash("Exista deja utilizatori.", "info")
        return redirect(url_for("crud_list", table="utilizator"))

    run_execute(
        "INSERT INTO utilizator (username, parola, email, rol) VALUES (%s, %s, %s, %s);",
        ("admin", "hash_admin", "admin@clinica.ro", "admin")
    )
    flash("Admin demo creat (admin).", "success")
    return redirect(url_for("crud_list", table="utilizator"))


@app.route("/crud/<table>")
def crud_list(table):
    cfg = ensure_table_allowed(table)
    cols, rows = fetch_list(table)
    return render_template(
        "crud_list.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        cols=cols,
        rows=rows,
    )


@app.route("/crud/<table>/create", methods=["GET", "POST"])
def crud_create(table):
    cfg = ensure_table_allowed(table)
    fk_options = build_fk_options(cfg)

    if request.method == "POST":
        try:
            insert_record(table, request.form)
            flash("Creat cu succes.", "success")
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")

    return render_template(
        "crud_form.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        mode="create",
        fields=cfg["create_fields"],
        values={},
        fk_options=fk_options,
        choices=cfg.get("choices", {}),
    )


@app.route("/crud/<table>/edit/<int:rec_id>", methods=["GET", "POST"])
def crud_edit(table, rec_id):
    cfg = ensure_table_allowed(table)
    cols, row = fetch_by_id(table, rec_id)
    if not row:
        abort(404)

    values = dict(zip(cols, row))
    fk_options = build_fk_options(cfg)

    if request.method == "POST":
        try:
            update_record(table, rec_id, request.form)
            flash("Update reusit.", "success")
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")

    return render_template(
        "crud_form.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        mode="edit",
        fields=cfg["update_fields"],
        values=values,
        fk_options=fk_options,
        choices=cfg.get("choices", {}),
        rec_id=rec_id,
    )


@app.route("/crud/<table>/delete/<int:rec_id>", methods=["POST"])
def crud_delete(table, rec_id):
    ensure_table_allowed(table)
    try:
        delete_record_safe(table, rec_id)
        flash("Sters cu succes!", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("crud_list", table=table))


@app.route("/search", methods=["GET", "POST"])
def search():
    result = None
    if request.method == "POST":
        table = (request.form.get("table") or "").strip()
        field = (request.form.get("field") or "").strip()
        value = (request.form.get("value") or "").strip()
        try:
            ensure_table_allowed(table)
            exists = record_exists(table, field, value)
            result = {"ok": True, "exists": exists, "table": table, "field": field, "value": value}
        except Exception as e:
            result = {"ok": False, "error": str(e)}

    return render_template("search.html", site_cfg=CRUD_CONFIG, result=result)


if __name__ == "__main__":
    app.run(debug=True,port=5001)