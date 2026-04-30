from app.db import run_execute, run_select
from datetime import date, timedelta

pacient_id = run_select("SELECT id_pacient FROM pacient LIMIT 1;")[0][0]
medic_id = run_select("SELECT id_medic FROM medic LIMIT 1;")[0][0]
data_viitoare = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
data_trecuta = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')

print("TEST TRIGGER BEFORE INSERT (programare)")
print("Inserare valida (data = " + data_viitoare + ")")
try:
    run_execute(
        sql="INSERT INTO programare (data, ora, cabinet, id_pacient, id_medic) VALUES (%s, %s, %s, %s, %s);",
        params=(data_viitoare, "12:00:00", "C1", pacient_id, medic_id)
    )
    print("OK: Inserarea valida a reusit")
except Exception as e:
    print("EROARE (nu trebuia):", e)

print("\nInserare invalida (data = " + data_trecuta + ")")
try:
    run_execute(
        sql="INSERT INTO programare (data, ora, cabinet, id_pacient, id_medic) VALUES (%s, %s, %s, %s, %s);",
        params=(data_trecuta, "12:00:00", "C1", pacient_id, medic_id)
    )
    print("EROARE: Inserarea invalida a trecut (trigger NU functioneaza)")
except Exception as e:
    print("OK: Inserarea invalida a fost respinsa de trigger")
    print("Mesaj DB:", e)

print("\nTEST TRIGGER AFTER UPDATE (programare)")
print("Facem update pe status")

prog_id = run_select("SELECT id_programare FROM programare ORDER BY id_programare DESC LIMIT 1;")[0][0]

run_execute(
    sql="UPDATE programare SET status = %s WHERE id_programare = %s;",
    params=("anulata", prog_id)
)

print("Verificam log-urile")
logs = run_select("SELECT actiune FROM user_log ORDER BY id_log DESC LIMIT 3;")
for l in logs:
    print("-", l[0])

print("\nTEST TRIGGER AFTER INSERT (consultatie)")
run_execute(
    sql="INSERT INTO consultatie (id_programare, diagnostic, cost) VALUES (%s, %s, %s);",
    params=(prog_id, "Control", 50.0)
)
status_final = run_select("SELECT status FROM programare WHERE id_programare = %s;", params=(prog_id,))[0][0]
print("- Status programare dupa consultatie:", status_final)

print("\nTEST TRIGGERE FINALIZAT")