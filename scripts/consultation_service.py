import json
from app.db import get_connection, run_select

print("=== TESTARE COMPLETA: PROGRAMARI SI CONSULTATII ===\n")

# Presupunem că ai deja în baza de date un pacient cu ID 1 și un medic cu ID 1
id_pacient = 1
id_medic = 1
cabinet = "Cabinet Cardiologie 1"

conn = get_connection()
cur = conn.cursor()

try:
    print("--- 1. Creare Programare Nouă ---")
    cur.execute(
        "CALL gestionare_programare(%s, %s, %s, %s, %s, %s, %s);",
        ('creare', None, '2026-05-20', '10:00:00', cabinet, id_pacient, id_medic)
    )

    # Preluam ID-ul noii programări
    row = cur.fetchone()
    id_programare_noua = row[0]

    while cur.nextset():
        if cur.description is not None:
            cur.fetchall()

    conn.commit()
    print(f"OK: Programare creată cu succes. ID_Programare = {id_programare_noua}")

    print("\n--- 2. Reprogramare ---")
    cur.execute(
        "CALL gestionare_programare(%s, %s, %s, %s, %s, %s, %s);",
        ('reprogramare', id_programare_noua, '2026-05-22', '14:30:00', cabinet, id_pacient, id_medic)
    )

    row = cur.fetchone()
    while cur.nextset():
        if cur.description is not None:
            cur.fetchall()

    conn.commit()
    print(f"OK: Programarea {id_programare_noua} a fost reprogramată pentru data de 2026-05-22.")

    print("\n--- 3. Finalizare Consultatie & Emitere Factură ---")
    diagnostic = "Control de rutina"
    analize_recomandate = "Hemoleucograma completa"
    recomandari_tratament = "Vitamina C, repaus"

    servicii = [
        {"cod": "CONS-001", "qty": 1},
        {"cod": "LAB-SANG-001", "qty": 1}
    ]
    servicii_json = json.dumps(servicii)

    # Folosim id_programare_noua pentru a asigura o relație 1:1 unică
    cur.execute(
        "CALL finalizare_consultatie(%s, %s, %s, %s, %s);",
        (id_programare_noua, diagnostic, analize_recomandate, recomandari_tratament, servicii_json)
    )

    row = cur.fetchone()
    id_consultatie = row[0]

    while cur.nextset():
        if cur.description is not None:
            cur.fetchall()

    conn.commit()
    print(f"OK: Consultatie finalizata cu succes. ID_Consultatie = {id_consultatie}")

except Exception as e:
    conn.rollback()
    print(f"\nEroare la executia procedurilor: {e}")
    raise
finally:
    cur.close()
    conn.close()

print("\n=== VERIFICARE IN BAZA DE DATE ===")

print("\n1. Date Programare (Atenție la Status):")
rows_prog = run_select("""
    SELECT p.id_programare, p.data, p.ora, p.status, m.nume_medic, pac.nume AS nume_pacient
    FROM programare p
    JOIN medic m ON m.id_medic = p.id_medic
    JOIN pacient pac ON pac.id_pacient = p.id_pacient
    WHERE p.id_programare = %s;
""", (id_programare_noua,))
for r in rows_prog:
    print(r)

print("\n2. Detalii Factură (Servicii medicale prestate):")
rows_fact = run_select("""
    SELECT f.id_consultatie, s.cod_serviciu, s.denumire, f.cantitate, f.pret_unitar, (f.cantitate * f.pret_unitar) AS total_linie
    FROM factura f
    JOIN servicii_medicale s ON s.id_serviciu = f.id_serviciu
    WHERE f.id_consultatie = %s
    ORDER BY s.cod_serviciu;
""", (id_consultatie,))
for r in rows_fact:
    print(r)

print("\n3. Cost Total (Tabela Consultatie):")
rows_cost = run_select("SELECT cost FROM consultatie WHERE id_consultatie = %s;", (id_consultatie,))
if rows_cost:
    print(f"Total de plată calculat: {rows_cost[0][0]} RON")