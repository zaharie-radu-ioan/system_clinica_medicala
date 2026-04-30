import csv
from pathlib import Path
from app.db import get_connection

ALLOWED_TABLES = {
    "utilizator", "medic", "pacient", "dosar_medical", "programare",
    "user_log", "consultatie", "servicii_medicale", "factura",
    "medicament", "reteta", "reteta_medicament", "notificare"
}


# Detecteaza dinamic coloanele AUTO_INCREMENT
def get_table_info(cur, table: str):
    cur.execute(f"DESCRIBE {table};")
    valid_cols = set()
    dynamic_skip_cols = {"created_at"}  # Ignoram timestamp-ul pentru autogenerare

    for row in cur.fetchall():
        col_name = row[0]
        extra = row[5] if len(row) > 5 else ""  # Extragem detaliile coloanei
        valid_cols.add(col_name)

        # Adaugam auto_increment in lista de ignorare
        if extra and 'auto_increment' in extra.lower():
            dynamic_skip_cols.add(col_name)

    return valid_cols, dynamic_skip_cols


def import_table_from_csv(table: str, csv_path: Path, truncate_first: bool = False):
    table = table.strip()
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Tabel invalid. Alege din: {sorted(ALLOWED_TABLES)}")

    if not csv_path.exists():
        raise FileNotFoundError(f"Nu exista CSV: {csv_path}")

    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    skipped = 0

    try:
        # Aflam coloanele tabelului curent
        table_cols, dynamic_skip_cols = get_table_info(cur, table)

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV invalid: lipseste header-ul.")

            cols = []
            for c in reader.fieldnames:
                c = c.strip()
                if c in dynamic_skip_cols:
                    continue  # Sarim peste coloanele protejate
                if c in table_cols:
                    cols.append(c)  # Adaugam coloanele valide

            if not cols:
                raise ValueError("Nu am coloane importabile.")

            placeholders = ",".join(["%s"] * len(cols))
            col_list = ",".join(cols)

            # INSERT IGNORE pentru a evita erorile la duplicate
            sql = f"INSERT IGNORE INTO {table} ({col_list}) VALUES ({placeholders});"

            conn.begin()

            if truncate_first:
                cur.execute(f"TRUNCATE TABLE {table};")

            for i, row in enumerate(reader, start=2):
                values = []
                empty_row = True
                for c in cols:
                    val = row.get(c)
                    val = val.strip() if val is not None else ""
                    if val != "":
                        empty_row = False
                    values.append(val if val != "" else None)

                if empty_row:
                    skipped += 1
                    continue

                cur.execute(sql, tuple(values))
                inserted += cur.rowcount  # Numaram doar randurile inserate efectiv

            conn.commit()
            print(f"IMPORT OK -> table={table}, inserted={inserted}, skipped={skipped}")

    except Exception as e:
        conn.rollback()
        print(f"IMPORT FAIL -> rollback. Eroare: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    t_name = input(f"Tabel ({', '.join(sorted(ALLOWED_TABLES))}): ").strip()
    p_str = input("Cale CSV (ex: exports/medic.csv): ").strip()
    trunc = input("TRUNCATE inainte? (y/n): ").strip().lower() == "y"
    import_table_from_csv(t_name, Path(p_str), truncate_first=trunc)