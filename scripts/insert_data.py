from app.db import run_execute, run_select

# --- 1. INSERARE PACIENT ---
print("Inseram cont utilizator si profil pacient...")

# Pasul A: Cream contul de login
run_execute(sql="INSERT INTO utilizator (username, parola, rol) VALUES (%s, %s, %s);",
            params=("ion_popescu", "parola123", "pacient"))

# Pasul B: Luam ID-ul contului creat
u_pacient_id = run_select(sql="SELECT id_utilizator FROM utilizator WHERE username=%s;", params=("ion_popescu",))[0][0]

# Pasul C: Cream profilul de pacient legat de acest cont
run_execute(sql="""INSERT INTO pacient (id_utilizator, nume, prenume, CNP, data_nasterii, sex, telefon) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s);""",
            params=(u_pacient_id, "Popescu", "Ion", "1800515123456", "1980-05-15", "Masculin", "0722111222"))


# --- 2. INSERARE MEDIC ---
print("Inseram cont utilizator si profil medic...")

# Pasul A: Cream contul medicului
run_execute(sql="INSERT INTO utilizator (username, parola, rol) VALUES (%s, %s, %s);",
            params=("dr_ionescu", "med789", "medic"))

# Pasul B: Luam ID-ul contului
u_medic_id = run_select(sql="SELECT id_utilizator FROM utilizator WHERE username=%s;", params=("dr_ionescu",))[0][0]

# Pasul C: Cream profilul de medic
run_execute(sql="""INSERT INTO medic (id_utilizator, nume_medic, cod_parafa, specializare, program) 
                   VALUES (%s, %s, %s, %s, %s);""",
            params=(u_medic_id, "Dr. Ionescu", 823456, "Cardiologie", "L-V: 08:00-14:00"))


# --- 3. INSERARE PROGRAMARE ---
print("Inseram programari...")

# Avem nevoie de ID-ul de profil (id_pacient si id_medic) pentru tabelul programare
p_id = run_select(sql="SELECT id_pacient FROM pacient WHERE CNP=%s;", params=("1800515123456",))[0][0]
m_id = run_select(sql="SELECT id_medic FROM medic WHERE cod_parafa=%s;", params=(823456,))[0][0]

run_execute(sql="INSERT INTO programare (data, ora, cabinet, id_pacient, id_medic, status) VALUES (%s, %s, %s, %s, %s, %s);",
            params=("2026-04-10", "10:30:00", "Cabinet 102", p_id, m_id, "programata"))


# --- 4. INSERARE LOG-URI ---
print("Inseram log-uri...")

# Acum log-urile se leaga de id_utilizator (contul central), nu de id_pacient
run_execute(sql="INSERT INTO user_log (id_utilizator, actiune) VALUES (%s, %s);",
            params=(u_pacient_id, "LOGIN_SUCCESS"))
run_execute(sql="INSERT INTO user_log (id_utilizator, actiune) VALUES (%s, %s);",
            params=(u_pacient_id, "APPOINTMENT_SCHEDULED"))

print("Datele au fost inserate cu succes conform noii arhitecturi!")