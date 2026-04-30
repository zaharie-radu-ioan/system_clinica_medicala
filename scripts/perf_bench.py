import time
import statistics
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from app.db import run_select, run_execute

# === CONFIGURARE TEST ===
RUNS = 30  # Numarul de repetari pentru fiecare test
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
CHART_FILE = OUTPUT_DIR / "performanta_clinica.png"
REPORT_FILE = OUTPUT_DIR / "raport_performanta.txt"

# 1. QUERY-URILE DE TEST
TEST_QUERIES = [
    {
        "name": "Istoric Pacient (ID)",
        "sql": "SELECT * FROM programare WHERE id_pacient = %s;",
        "params": (1,),
    },
    {
        "name": "Cautare Medic (Specializare)",
        "sql": "SELECT * FROM medic WHERE specializare = %s;",
        "params": ("Cardiologie",),
    },
    {
        "name": "Calendar (Data)",
        "sql": "SELECT * FROM programare WHERE data = %s;",
        "params": ("2026-04-06",),
    },
    {
        "name": "Cautare Pacient (Nume/Prenume)",
        "sql": "SELECT * FROM pacient WHERE nume = %s AND prenume = %s;",
        "params": ("Popescu", "Ion"),
    },
    {
        "name": "Filtrare Status Programari",
        "sql": "SELECT * FROM programare WHERE status = %s;",
        "params": ("anulata",),
    },
    {
        "name": "Audit Activitate Utilizator",
        "sql": "SELECT * FROM user_log WHERE id_utilizator = %s;",
        "params": (1,),
    }
]

DROP_INDEX_SQL = [
    "DROP INDEX IF EXISTS idx_programare_pacient ON programare;",
    "DROP INDEX IF EXISTS idx_medic_specializare ON medic;",
    "DROP INDEX IF EXISTS idx_programare_data ON programare;",
    "DROP INDEX IF EXISTS idx_pacient_nume_prenume ON pacient;",
    "DROP INDEX IF EXISTS idx_programare_status ON programare;",
    "DROP INDEX IF EXISTS idx_consultatie_data ON consultatie;",
    "DROP INDEX IF EXISTS idx_user_log_utilizator ON user_log;",
    "DROP INDEX IF EXISTS idx_user_log_data ON user_log;"
]

APPLY_INDEX_SQL = [
    "CREATE OR REPLACE INDEX idx_programare_pacient ON programare(id_pacient);",
    "CREATE OR REPLACE INDEX idx_medic_specializare ON medic(specializare);",
    "CREATE OR REPLACE INDEX idx_programare_data ON programare(data);",
    "CREATE OR REPLACE INDEX idx_pacient_nume_prenume ON pacient(nume, prenume);",
    "CREATE OR REPLACE INDEX idx_programare_status ON programare(status);",
    "CREATE OR REPLACE INDEX idx_consultatie_data ON consultatie(created_at);",
    "CREATE OR REPLACE INDEX idx_user_log_utilizator ON user_log(id_utilizator);",
    "CREATE OR REPLACE INDEX idx_user_log_data ON user_log(created_at);"
]

def benchmark_query(sql, params, runs):
    durations = []
    for _ in range(runs):
        start = time.perf_counter()
        run_select(sql, params)
        end = time.perf_counter()
        durations.append((end - start) * 1000)
    return statistics.mean(durations)

def run_suite(label):
    print(f"\n--- Rulam testele: {label} ---")
    results = {}
    for q in TEST_QUERIES:
        avg_time = benchmark_query(q["sql"], q["params"], RUNS)
        results[q["name"]] = avg_time
        print(f" > {q['name']}: {avg_time:.4f} ms")
    return results

def generate_chart(before_results, after_results):
    labels = list(before_results.keys())
    before_means = [before_results[name] for name in labels]
    after_means = [after_results[name] for name in labels]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 8))
    rects1 = ax.bar(x - width/2, before_means, width, label='Inainte de Index', color='#e74c3c')
    rects2 = ax.bar(x + width/2, after_means, width, label='Dupa Index', color='#2ecc71')

    ax.set_ylabel('Timp mediu (ms)')
    ax.set_title('Impactul Indexarii asupra Performantei Clinicii')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha='right')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    ax.bar_label(rects1, padding=3, fmt='%.3f')
    ax.bar_label(rects2, padding=3, fmt='%.3f')

    fig.tight_layout()
    plt.savefig(CHART_FILE)
    plt.show()

def main():
    print("=== START BENCHMARK: ANALIZA INDEXURI CLINICA ===")

    # PAS 1: BEFORE
    print("\n[1/3] Curatam indexurile pentru testul 'BEFORE'...")
    for stmt in DROP_INDEX_SQL:
        try:
            run_execute(stmt)
        except Exception as e:
            print(f"Ignoram eroare drop: {e}")

    before_results = run_suite("BEFORE")

    # PAS 2: AFTER
    print("\n[2/3] Aplicam cele 8 indexuri de optimizare...")
    for stmt in APPLY_INDEX_SQL:
        run_execute(stmt)

    after_results = run_suite("AFTER")

    # PAS 3: RAPORT
    print("\n[3/3] Generam raportul final...")
    report = ["=== RAPORT PERFORMANTA CLINICA ===\n"]
    for name in before_results:
        b, a = before_results[name], after_results[name]
        improvement = ((b - a) / b) * 100 if b > 0 else 0
        report.append(f"{name}: {b:.4f}ms -> {a:.4f}ms | Imbunatatire: {improvement:.1f}%")

    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")
    print(f"Raport salvat in: {REPORT_FILE}")

    generate_chart(before_results, after_results)

if __name__ == "__main__":
    main()