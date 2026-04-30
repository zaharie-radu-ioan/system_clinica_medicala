import json
from pathlib import Path
from app.db import run_select

MIN_PROG = 5

sql = """
    SELECT
        m.id_medic,
        m.nume_medic,
        m.specializare,
        COUNT(c.id_consultatie) AS consultatii_finalizate,
        COALESCE(SUM(c.cost), 0) AS venit_total
    FROM medic m
    LEFT JOIN programare p ON m.id_medic = p.id_medic
    LEFT JOIN consultatie c ON p.id_programare = c.id_programare
    GROUP BY 
        m.id_medic,
        m.nume_medic,
        m.specializare
    HAVING COUNT(c.id_consultatie) > %s
    ORDER BY venit_total DESC;
"""

rows = run_select(sql, (MIN_PROG,))

data = []

for row in rows:
    data.append({
        "id_medic": row[0],
        "nume_medic": row[1],
        "specializare": row[2],
        "consultatii_finalizate": row[3],
        "venit_total": float(row[4])
    })

# 3. Creăm folderul output dacă nu există (pentru a evita eroarea de FileNotFoundError)
out_path = Path("../output") / "performanta_medici_filtered.json"

out_path.write_text(json.dumps({
    "min_consultatii_necesare": MIN_PROG,
    "results": data
}, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"JSON salvat: {out_path}")