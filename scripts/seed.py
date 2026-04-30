import random
import datetime
from faker import Faker
from app.db import run_execute, run_select

fake = Faker('ro_RO')

NUM_MEDICI = 500
NUM_PACIENTI = 1000
NUM_PROGRAMARI = 2000

simple_passwords = ["ananas", "parola123", "qwerty", "qwerty2024", "student123", "password", "abc123", "test123",
                    "letmein", "miruna2024"]

specializari = [
    "Cardiologie", "Dermatologie", "Neurologie", "Pediatrie", "Gastroenterologie", "Oftalmologie",
    "ORL", "Endocrinologie", "Ginecologie", "Urologie", "Ortopedie", "Pneumologie",
    "Reumatologie", "Psihiatrie", "Oncologie", "Nefrologie", "Hematologie", "Medicină Internă", "Radiologie"
]

variante_program = [
    "L-V: 08:00 - 14:00", "L-V: 14:00 - 20:00", "L, Mi, V: 08:00 - 16:00",
    "Ma, Jo: 10:00 - 18:00", "L-Mi: 09:00 - 13:00 / Jo-V: 14:00 - 18:00",
    "S-D: 09:00 - 15:00", "L, Ma, Jo: 08:00 - 15:00", "Mi, V: 12:00 - 20:00"
]

DATE_MEDICALE = {
    "Cardiologie": {"diagnostice": ["Hipertensiune stadiul 1", "Insuficiență cardiacă", "Fibrilație atrială"],
                    "tratamente": ["Amlodipină 5mg", "Bisoprolol 5mg", "Rosuvastatină 10mg"],
                    "analize": ["EKG de repaus", "Ecocardiografie", "Holter EKG"]},
    "Dermatologie": {"diagnostice": ["Acnee vulgară", "Psoriazis în plăci", "Eczemă atopică"],
                     "tratamente": ["Cremă cu hidrocortizon", "Unguent clotrimazol", "Fără tratament"],
                     "analize": ["Dermatoscopie", "Biopsie cutanată", "Examen micologic"]},
    "Neurologie": {"diagnostice": ["Migrenă cu aură", "Lombosciatică", "Spondiloză cervicală"],
                   "tratamente": ["Ibuprofen 400mg", "Gabapentin 300mg", "Complex Vitamina B"],
                   "analize": ["RMN cerebral", "RMN coloană", "Doppler vase cervicale"]},
    "Pediatrie": {"diagnostice": ["Viroză respiratorie", "Otită medie", "Faringoamigdalită"],
                  "tratamente": ["Paracetamol sirop", "Hidratare intensivă", "Antibiotic suspensie"],
                  "analize": ["Hemoleucogramă", "Exudat faringian", "Test gripă"]},
    "Gastroenterologie": {"diagnostice": ["BRGE", "Sindrom dispeptic", "Steatoză hepatică"],
                          "tratamente": ["Omeprazol 20mg", "No-Spa 40mg", "Regim alimentar"],
                          "analize": ["Ecografie abdominală", "Endoscopie", "Test Helicobacter"]},
    "Oftalmologie": {"diagnostice": ["Conjunctivită bacteriană", "Cataractă senilă", "Miopie"],
                     "tratamente": ["Picături cu Tobramicină", "Prescripție ochelari", "Operație recomandată"],
                     "analize": ["Acuitate vizuală", "Tensiune oculară", "OCT"]},
    "ORL": {"diagnostice": ["Sinuzită maxilară", "Deviație de sept", "Laringită"],
            "tratamente": ["Antibioterapie", "Fluticazonă spray", "Repaus vocal"],
            "analize": ["Exudat nazal", "Radiografie sinusuri", "Fibroscopie"]},
    "Endocrinologie": {"diagnostice": ["Hipotiroidism", "Hipertiroidism", "Obezitate"],
                       "tratamente": ["Eutirox 50mcg", "Dietă hipocalorică", "Vitamina D3"],
                       "analize": ["TSH, FT4", "Ecografie tiroidiană", "Glicemie a jeun"]},
    "Ginecologie": {"diagnostice": ["Control de rutină", "Vaginită micotică", "Sarcina trimestrul I"],
                    "tratamente": ["Ovule antifungice", "Vitamine prenatale", "Contraceptive"],
                    "analize": ["Ecografie transvaginală", "Test Babeș-Papanicolau", "Examen secreție"]},
    "Urologie": {"diagnostice": ["Infecție urinară", "Litiază renală", "Hiperplazie prostată"],
                 "tratamente": ["Ciprofloxacină 500mg", "Tamsulosin 0.4mg", "Hidratare intensă"],
                 "analize": ["Urocultură", "Ecografie renală", "PSA total"]},
    "Ortopedie": {"diagnostice": ["Entorsă gleznă", "Osteoartrită genunchi", "Lombalgie mecanică"],
                  "tratamente": ["Gheață și repaus", "Diclofenac gel", "Kinetoterapie"],
                  "analize": ["Radiografie articulație", "RMN genunchi", "Ecografie mușchi"]},
    "Pneumologie": {"diagnostice": ["Astm bronșic", "BPOC", "Apnee în somn"],
                    "tratamente": ["Salbutamol inhalator", "Antibiotic macrolid", "Aparat CPAP"],
                    "analize": ["Spirometrie", "Radiografie pulmonară", "Pulsoximetrie"]},
    "Reumatologie": {"diagnostice": ["Poliartrită reumatoidă", "Osteoporoză", "Gută"],
                     "tratamente": ["Metotrexat", "Calciu + Vitamina D3", "Antiinflamatoare"],
                     "analize": ["VSH, CRP", "Factor reumatoid", "Osteodensitometrie (DEXA)"]},
    "Psihiatrie": {"diagnostice": ["Episod depresiv", "Anxietate generalizată", "Burnout"],
                   "tratamente": ["Sertralină 50mg", "Alprazolam", "Psihoterapie"],
                   "analize": ["Consult psihologic", "Scală depresie", "Fără analize lab"]},
    "Oncologie": {"diagnostice": ["Neoplasm în observație", "Anemie secundară", "Tumoră benignă"],
                  "tratamente": ["Chimioterapie", "Tratament paliativ", "Monitorizare 6 luni"],
                  "analize": ["Markeri tumorali", "CT torace-abdomen", "Biopsie"]},
    "Nefrologie": {"diagnostice": ["Boală cronică rinichi", "Pielonefrită", "Sindrom nefrotic"],
                   "tratamente": ["Dietă hipoproteică", "Antibioterapie", "Diuretice"],
                   "analize": ["Creatinină, Uree", "Clearance 24h", "Ecografie renală"]},
    "Hematologie": {"diagnostice": ["Anemie feriprivă", "Trombocitopenie", "Deficit B12"],
                    "tratamente": ["Fier 1 cp/zi", "Injecții B12", "Anticoagulant"],
                    "analize": ["Hemoleucogramă", "Sideremie, Feritină", "Timp protrombină"]},
    "Medicină Internă": {"diagnostice": ["Control de rutină", "Sindrom metabolic", "Infectie respiratorie"],
                         "tratamente": ["Complex vitamine", "Dietă echilibrată", "Paracetamol"],
                         "analize": ["Pachet uzual", "Ecografie abdominală", "EKG"]},
    "Radiologie": {"diagnostice": ["Examen imagistic normal", "Aspect post-traumatic", "Se recomandă corelare"],
                   "tratamente": ["Fără medicamente", "Revenire la medic", "Repaus fizic"],
                   "analize": ["RMN regiune", "CT cu contrast", "Radiografie standard"]}
}

# Catalog medicamente pentru retete
MEDICAMENTE = [
    ("Paracetamol 500mg", "comprimate"),
    ("Ibuprofen 400mg", "comprimate"),
    ("Amoxicilină 500mg", "capsule"),
    ("Ciprofloxacină 500mg", "comprimate"),
    ("Omeprazol 20mg", "capsule"),
    ("Metformin 500mg", "comprimate"),
    ("Atorvastatină 20mg", "comprimate"),
    ("Bisoprolol 5mg", "comprimate"),
    ("Amlodipină 5mg", "comprimate"),
    ("Enalapril 10mg", "comprimate"),
    ("Sertralină 50mg", "comprimate"),
    ("Alprazolam 0.25mg", "comprimate"),
    ("Gabapentin 300mg", "capsule"),
    ("Diclofenac gel 1%", "gel"),
    ("Hidrocortizon cremă 1%", "cremă"),
    ("Salbutamol 100mcg", "inhalator"),
    ("Fluticazonă 50mcg", "spray nazal"),
    ("Eutirox 50mcg", "comprimate"),
    ("Vitamina D3 2000UI", "comprimate"),
    ("Vitamina B12 1mg", "comprimate"),
    ("Calciu 500mg + D3", "comprimate"),
    ("Fier II fumarat 200mg", "comprimate"),
    ("Tamsulosin 0.4mg", "capsule retard"),
    ("Metotrexat 2.5mg", "comprimate"),
    ("No-Spa 40mg", "comprimate"),
    ("Tobramicină picături", "picături oftalmice"),
    ("Clotrimazol unguent 1%", "unguent"),
    ("Rosuvastatină 10mg", "comprimate"),
    ("Acid folic 5mg", "comprimate"),
    ("Paracetamol sirop 120mg/5ml", "sirop"),
]

DOZE = ["100mg", "200mg", "250mg", "400mg", "500mg", "1g", "5mg", "10mg", "20mg", "50mg"]
FRECVENTE = ["o dată pe zi", "de 2 ori pe zi", "de 3 ori pe zi", "la 8 ore", "la 12 ore", "seara la culcare"]
DURATE = ["5 zile", "7 zile", "10 zile", "14 zile", "30 zile", "continuu"]

# ============================================================
print("Cream user admin fix...")
# ============================================================
data_admin = fake.date_time_between(start_date='-7y', end_date='-4y')
run_execute(
    "INSERT INTO utilizator (username, parola, email, rol, created_at) VALUES (%s, %s, %s, %s, %s);",
    ("admin", "admin123", "admin@clinica.ro", "admin", data_admin)
)

# ============================================================
print("Generam catalog servicii medicale...")
# ============================================================
servicii_baza = [
    ("CONS-001", "Consultație inițială medic specialist", 250.00),
    ("CONS-002", "Consultație de control", 150.00),
    ("CONS-003", "Consultație medic primar", 300.00),
    ("CONS-004", "Consultație interdisciplinară", 400.00)
]

analize_sange = [
    "Hemoleucogramă", "VSH", "Glicemie", "Colesterol total", "HDL", "LDL", "Trigliceride",
    "TGO", "TGP", "GGT", "Bilirubină totală", "Bilirubină directă", "Creatinină", "Uree",
    "Acid uric", "Sodiu", "Potasiu", "Calciu seric", "Magneziu", "Fier", "Feritină",
    "TSH", "FT4", "Proteina C reactivă (CRP)", "Fibrinogen", "Timp Quick", "INR",
    "Hemoglobină glicozilată (HbA1c)", "Vitamina D", "Vitamina B12", "Acid folic"
]
for i, an in enumerate(analize_sange):
    servicii_baza.append((f"LAB-SANG-{i + 1:03d}", f"Analiză sânge: {an}", random.choice([30.00, 45.00, 60.00, 80.00])))

zone_imagistica = [
    "Cerebral", "Cervical", "Toracic", "Abdominal", "Pelvin", "Lombar",
    "Genunchi stâng", "Genunchi drept", "Umăr stâng", "Umăr drept",
    "Gleznă stângă", "Gleznă dreaptă", "Șold stâng", "Șold drept", "Părți moi", "Tiroidă"
]
for i, zona in enumerate(zone_imagistica):
    servicii_baza.append((f"RMN-N-{i + 1:03d}", f"RMN {zona} nativ", 600.00))
    servicii_baza.append((f"RMN-C-{i + 1:03d}", f"RMN {zona} cu contrast", 850.00))
    servicii_baza.append((f"CT-N-{i + 1:03d}", f"CT {zona} nativ", 350.00))
    servicii_baza.append((f"CT-C-{i + 1:03d}", f"CT {zona} cu contrast", 550.00))
    servicii_baza.append((f"ECO-{i + 1:03d}", f"Ecografie {zona}", 220.00))
    servicii_baza.append((f"RX-{i + 1:03d}", f"Radiografie {zona}", 120.00))

alergeni = [
    "Arahide", "Lapte vacă", "Ou", "Soia", "Grâu", "Praf de casă", "Acarieni",
    "Polen graminee", "Polen ambrozie", "Venin albină", "Venin viespe",
    "Păr pisică", "Păr câine", "Mucegai", "Penicilină", "Ibuprofen", "Aspirină"
]
for i, alg in enumerate(alergeni):
    servicii_baza.append((f"ALG-{i + 1:03d}", f"Test alergeni IgE - {alg}", 75.00))

proceduri_diverse = [
    ("Kinetoterapie (ședință)", 120.00), ("Masaj terapeutic", 100.00),
    ("Infiltrație articulară", 250.00), ("Sutură plagă simplă", 150.00),
    ("Extracție fire sutură", 60.00), ("Spălătură auriculară", 80.00),
    ("Dermatoscopie (max 3 leziuni)", 180.00), ("Montare Holter EKG", 200.00),
    ("Montare Holter TA", 150.00), ("EKG de repaus", 80.00),
    ("Injecție intramusculară", 40.00), ("Perfuzie (fără medicație)", 100.00)
]
for i, (nume, pret) in enumerate(proceduri_diverse):
    servicii_baza.append((f"PROC-{i + 1:03d}", nume, pret))

for cod, denumire, pret in servicii_baza:
    try:
        run_execute("INSERT INTO servicii_medicale (cod_serviciu, denumire, pret) VALUES (%s, %s, %s);",
                    (cod, denumire, pret))
    except Exception:
        pass

print(f"-> S-au generat {len(servicii_baza)} servicii medicale unice.")

# ============================================================
print("Generam catalog medicamente...")
# ============================================================
for denumire, forma in MEDICAMENTE:
    try:
        run_execute(
            "INSERT INTO medicament (denumire, forma) VALUES (%s, %s);",
            (denumire, forma)
        )
    except Exception:
        pass

toate_medicamentele = run_select("SELECT id_medicament FROM medicament;")
print(f"-> S-au generat {len(toate_medicamentele)} medicamente.")

# ============================================================
print("Generam medici...")
# ============================================================
lista_parafa = random.sample(range(100000, 999999), NUM_MEDICI)
for i in range(NUM_MEDICI):
    nume_m, prenume_m = fake.last_name(), fake.first_name()
    email_medic = f"dr.{nume_m.lower()}.{prenume_m.lower()}_{random.randint(1, 999)}@clinica.ro"
    run_execute(
        "INSERT INTO utilizator (username, parola, email, rol, created_at) VALUES (%s, %s, %s, %s, %s);",
        (f"dr_{nume_m.lower()}_{i}", random.choice(simple_passwords), email_medic, "medic",
         fake.date_time_between(start_date='-3y', end_date='now'))
    )
    user_id = run_select("SELECT id_utilizator FROM utilizator WHERE email=%s;", (email_medic,))[0][0]
    run_execute(
        "INSERT INTO medic (id_utilizator, nume_medic, cod_parafa, specializare, program) VALUES (%s, %s, %s, %s, %s);",
        (user_id, f"Dr. {nume_m} {prenume_m}", lista_parafa[i], random.choice(specializari),
         random.choice(variante_program))
    )

# ============================================================
print("Generam pacienti...")
# ============================================================
lista_cnp = random.sample(range(1000000000000, 2999999999999), NUM_PACIENTI)
for i in range(NUM_PACIENTI):
    gen = random.choice(["Masculin", "Feminin"])
    nume_p = fake.last_name()
    prenume_p = fake.first_name_male() if gen == "Masculin" else fake.first_name_female()
    email_p = f"p.{nume_p.lower()}.{prenume_p.lower()}_{i}@email.com"
    run_execute(
        "INSERT INTO utilizator (username, parola, email, rol, created_at) VALUES (%s, %s, %s, %s, %s);",
        (f"p_{nume_p.lower()}_{i}", random.choice(simple_passwords), email_p, "pacient",
         fake.date_time_between(start_date='-4y', end_date='now'))
    )
    user_id = run_select("SELECT id_utilizator FROM utilizator WHERE email=%s;", (email_p,))[0][0]
    run_execute(
        "INSERT INTO pacient (id_utilizator, nume, prenume, CNP, data_nasterii, sex, telefon) VALUES (%s, %s, %s, %s, %s, %s, %s);",
        (user_id, nume_p, prenume_p, str(lista_cnp[i]),
         fake.date_of_birth(minimum_age=1, maximum_age=98), gen, fake.phone_number())
    )

# ============================================================
print("Generam dosare medicale pentru pacienti...")
# ============================================================
toti_pacientii = run_select("SELECT id_pacient FROM pacient;")
grupe = ['A1', 'A2', 'B', 'AB', 'O']
rh_vals = ['+', '-']
alergii_posibile = ["Polen", "Penicilină", "Ibuprofen", "Aspirină", "Arahide", "Latex", "Praf de casă", None]
boli_posibile = ["Hipertensiune arterială", "Diabet zaharat tip 2", "Astm bronșic",
                 "Hipotiroidism", "Obezitate", "Cardiopatie ischemică", None]

for (id_p,) in toti_pacientii:
    alergie = random.choice(alergii_posibile)
    boala = random.choice(boli_posibile)
    run_execute(
        "INSERT INTO dosar_medical (id_pacient, grupa_sanguina, rh, alergii, boli_cronice) VALUES (%s, %s, %s, %s, %s);",
        (id_p, random.choice(grupe), random.choice(rh_vals), alergie, boala)
    )

print(f"-> S-au generat {len(toti_pacientii)} dosare medicale.")

# ============================================================
print("Generam programari...")
# ============================================================
medici_ids = run_select("SELECT id_medic FROM medic;")
pacienti_data = run_select("SELECT id_pacient, id_utilizator FROM pacient;")
today = datetime.date.today()

# Stergem toti triggerii care ar bloca inserturile cu date in trecut
run_execute("DROP TRIGGER IF EXISTS trg_programari_before_insert;")   # vechiul nume (pre-refactorizare)
run_execute("DROP TRIGGER IF EXISTS trg_programare_before_insert;")   # noul nume
run_execute("DROP TRIGGER IF EXISTS trg_verificare_suprapunere;")     # blocheaza duplicate ora/medic

for _ in range(NUM_PROGRAMARI):
    id_m = random.choice(medici_ids)[0]
    pac_ales = random.choice(pacienti_data)
    id_p, id_u = pac_ales[0], pac_ales[1]

    data_p = fake.date_between(start_date='-90d', end_date='+60d')
    ora_p = f"{random.randint(8, 19):02d}:{random.choice(['00', '15', '30', '45'])}"

    if data_p < today:
        status = random.choices(['finalizata', 'anulata'], weights=[85, 15], k=1)[0]
    elif data_p == today:
        status = random.choices(['finalizata', 'programata', 'anulata'], weights=[40, 50, 10], k=1)[0]
    else:
        status = random.choices(['programata', 'anulata'], weights=[85, 15], k=1)[0]

    run_execute(
        "INSERT INTO programare (data, ora, cabinet, id_pacient, id_medic, id_utilizator, status) VALUES (%s, %s, %s, %s, %s, %s, %s);",
        (data_p, ora_p, f"Cabinet {random.randint(1, 25)}", id_p, id_m, id_u, status)
    )

# Recrram triggerii dupa ce s-au inserat toate datele de test
run_execute("""
CREATE TRIGGER trg_programare_before_insert
BEFORE INSERT ON programare
FOR EACH ROW
BEGIN
    IF TIMESTAMP(NEW.data, NEW.ora) < NOW() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Eroare: Nu poti crea o programare in trecut.';
    END IF;
END;
""")

run_execute("""
CREATE TRIGGER trg_verificare_suprapunere
BEFORE INSERT ON programare
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count
    FROM programare
    WHERE id_medic = NEW.id_medic
      AND data     = NEW.data
      AND ora      = NEW.ora
      AND status  != 'anulata';
    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Eroare: Medicul are deja o programare la aceasta ora.';
    END IF;
END;
""")

# ============================================================
print("Generam consultatii si facturi...")
# ============================================================
prog_fin = run_select(
    """SELECT p.id_programare, p.data, m.specializare, pac.id_utilizator
       FROM programare p
       JOIN medic m   ON p.id_medic   = m.id_medic
       JOIN pacient pac ON p.id_pacient = pac.id_pacient
       WHERE p.status = 'finalizata';"""
)

toate_serviciile = run_select("SELECT id_serviciu, pret FROM servicii_medicale;")

for pf in prog_fin:
    id_programare = pf[0]
    data_prog = pf[1]
    specializare = pf[2]
    id_utilizator_pacient = pf[3]

    d_spec = DATE_MEDICALE.get(specializare, DATE_MEDICALE["Medicină Internă"])
    dt_c = datetime.datetime.combine(data_prog, datetime.time(random.randint(8, 19), random.randint(0, 59)))

    nr_servicii = random.randint(1, 4)
    servicii_alese = random.sample(toate_serviciile, nr_servicii)

    cost_total = 0.0
    linii_factura = []
    for serv in servicii_alese:
        id_serviciu = serv[0]
        pret_unitar = float(serv[1])
        cantitate = random.choices([1, 2, 3], weights=[85, 10, 5], k=1)[0]
        cost_total += pret_unitar * cantitate
        linii_factura.append((id_serviciu, cantitate, pret_unitar))

    run_execute(
        "INSERT INTO consultatie (id_programare, diagnostic, analize_recomandate, recomandari_tratament, cost, created_at) VALUES (%s, %s, %s, %s, %s, %s);",
        (id_programare, random.choice(d_spec["diagnostice"]), random.choice(d_spec["analize"]),
         random.choice(d_spec["tratamente"]), cost_total, dt_c)
    )

    id_cons_row = run_select("SELECT id_consultatie FROM consultatie WHERE id_programare = %s;", (id_programare,))
    if not id_cons_row:
        continue

    id_consultatie = id_cons_row[0][0]

    for linie in linii_factura:
        run_execute(
            "INSERT INTO factura (id_consultatie, id_serviciu, cantitate, pret_unitar) VALUES (%s, %s, %s, %s);",
            (id_consultatie, linie[0], linie[1], linie[2])
        )

# ============================================================
print("Generam retete pentru consultatii finalizate...")
# ============================================================
toate_consultatiile = run_select("SELECT id_consultatie, created_at FROM consultatie;")

nr_retete = 0
for (id_consultatie, created_at) in toate_consultatiile:
    # ~60% din consultatii primesc reteta
    if random.random() > 0.60:
        continue

    data_emiterii = created_at.date() if hasattr(created_at, 'date') else created_at
    valabila_pana = data_emiterii + datetime.timedelta(days=random.choice([30, 60, 90]))

    run_execute(
        "INSERT INTO reteta (id_consultatie, data_emiterii, valabila_pana) VALUES (%s, %s, %s);",
        (id_consultatie, data_emiterii, valabila_pana)
    )

    id_reteta_row = run_select("SELECT id_reteta FROM reteta WHERE id_consultatie = %s;", (id_consultatie,))
    if not id_reteta_row:
        continue

    id_reteta = id_reteta_row[0][0]

    # Fiecare reteta are 1-3 medicamente
    nr_med = random.randint(1, 3)
    medicamente_alese = random.sample(toate_medicamentele, min(nr_med, len(toate_medicamentele)))
    for (id_med,) in medicamente_alese:
        run_execute(
            "INSERT INTO reteta_medicament (id_reteta, id_medicament, doza, frecventa, durata) VALUES (%s, %s, %s, %s, %s);",
            (id_reteta, id_med, random.choice(DOZE), random.choice(FRECVENTE), random.choice(DURATE))
        )

    nr_retete += 1

print(f"-> S-au generat {nr_retete} retete cu medicamente.")

# ============================================================
print("Generam notificari...")
# ============================================================
toti_utilizatorii = run_select("SELECT id_utilizator FROM utilizator;")
tipuri_mesaje = {
    "reminder":    "Aveți o programare mâine la ora {ora}. Vă rugăm să confirmați prezența.",
    "confirmare":  "Programarea dumneavoastră din data {data} a fost confirmată cu succes.",
    "anulare":     "Programarea din data {data} a fost anulată. Puteți face o nouă programare oricând.",
    "sistem":      "Contul dumneavoastră a fost actualizat. Dacă nu recunoașteți această acțiune, contactați-ne.",
}

for _ in range(800):
    id_u = random.choice(toti_utilizatorii)[0]
    tip = random.choice(list(tipuri_mesaje.keys()))
    mesaj = tipuri_mesaje[tip].format(
        ora=f"{random.randint(8, 19):02d}:00",
        data=fake.date_between(start_date='-30d', end_date='+30d')
    )
    citita = random.choices([True, False], weights=[60, 40], k=1)[0]
    created_at = fake.date_time_between(start_date='-60d', end_date='now')
    run_execute(
        "INSERT INTO notificare (id_utilizator, mesaj, tip, citita, created_at) VALUES (%s, %s, %s, %s, %s);",
        (id_u, mesaj, tip, citita, created_at)
    )

print("-> S-au generat 800 notificari.")

# ============================================================
print("Generam log-uri random...")
# ============================================================
u_ids = run_select("SELECT id_utilizator FROM utilizator;")
for _ in range(500):
    run_execute(
        "INSERT INTO user_log (id_utilizator, actiune, ip_address, created_at) VALUES (%s, %s, %s, %s);",
        (random.choice(u_ids)[0], random.choice(["LOGIN", "LOGOUT", "VIEW_SCHEDULE"]),
         fake.ipv4(), fake.date_time_between(start_date='-60d', end_date='now'))
    )

print("--- Date generate cu succes! ---")