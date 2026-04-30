from app.db import run_execute
from scripts.create_tables import create_tables

print("--- Incepem procesul de Rebuild ---")

print("Stergem tabelele M:N si retete...")
run_execute("DROP TABLE IF EXISTS reteta_medicament;")
run_execute("DROP TABLE IF EXISTS reteta;")
run_execute("DROP TABLE IF EXISTS medicament;")

print("Stergem notificarile...")
run_execute("DROP TABLE IF EXISTS notificare;")

print("Stergem liniile de facturare si catalogul de servicii...")
run_execute("DROP TABLE IF EXISTS factura;")
run_execute("DROP TABLE IF EXISTS servicii_medicale;")

print("Stergem tabelele dependente (consultatie, user_log, programare)...")
run_execute("DROP TABLE IF EXISTS consultatie;")
run_execute("DROP TABLE IF EXISTS user_log;")
run_execute("DROP TABLE IF EXISTS programare;")

print("Stergem dosarele medicale...")
run_execute("DROP TABLE IF EXISTS dosar_medical;")

print("Stergem profilurile (medic, pacient)...")
run_execute("DROP TABLE IF EXISTS medic;")
run_execute("DROP TABLE IF EXISTS pacient;")

print("Stergem tabelul central de utilizatori...")
run_execute("DROP TABLE IF EXISTS utilizator;")

print("Creez tabelele din schema.sql conform noii structuri...")
create_tables()

print("--- Rebuild gata! Toate datele au fost resetate. ---")