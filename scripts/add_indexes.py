import time
from app.db import run_execute


def apply_indexes():
    print("=== APLICARE INDEXURI OPTIMIZARE (8 TOTAL) ===")

    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_programare_data ON programare(data);",
        "CREATE INDEX IF NOT EXISTS idx_pacient_nume_prenume ON pacient(nume, prenume);",
        "CREATE INDEX IF NOT EXISTS idx_medic_specializare ON medic(specializare);",
        "CREATE INDEX IF NOT EXISTS idx_user_log_utilizator ON user_log(id_utilizator);",
        "CREATE INDEX IF NOT EXISTS idx_user_log_data ON user_log(created_at);",

        "CREATE INDEX IF NOT EXISTS idx_programare_pacient ON programare(id_pacient);",
        "CREATE INDEX IF NOT EXISTS idx_programare_status ON programare(status);",
        "CREATE INDEX IF NOT EXISTS idx_consultatie_data ON consultatie(created_at);"
    ]

    for query in index_queries:
        print(f"Rulam: {query}")
        try:
            start_time = time.time()
            run_execute(query)
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            print(f"-> Succes! ({duration:.2f} ms)\n")
        except Exception as e:
            print(f"-> Info/Eroare: {e}\n")

    print("---------------------------------------------------------")
    print("Toate indexurile au fost procesate.")


if __name__ == "__main__":
    apply_indexes()