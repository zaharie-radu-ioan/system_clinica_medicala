import json
from pathlib import Path
from app.db import run_select

sql = """
    SELECT 
        m.id_medic,
        m.nume_medic,
        m.specializare,
        COALESCE(SUM(c.cost), 0) AS venit_total,

        COUNT(c.id_consultatie) AS consultatii_finalizate,
        COALESCE(
            (COUNT(c.id_consultatie) * 100.0 / 
            NULLIF(SUM(CASE WHEN p.status IN ('finalizata', 'anulata') THEN 1 ELSE 0 END), 0)), 
        0) AS rata_succes_procent
    FROM medic m
    LEFT JOIN programare p ON m.id_medic = p.id_medic
    LEFT JOIN consultatie c ON p.id_programare = c.id_programare
    GROUP BY 
        m.id_medic,
        m.nume_medic,
        m.specializare
    ORDER BY venit_total DESC;
"""

rows = run_select(sql)

data = []
for r in rows:
    data.append(
        {
            "id_medic": r[0],
            "nume_medic": r[1],
            "specializare": r[2],
            "performanta": {
                "venit_total": float(r[3]),
                "nr_consultatii": r[4],
                "rata_succes": round(float(r[5]), 2)
            }
        }
    )

out_path = Path("../output")/"performanta_medici.json"
out_path.parent.mkdir(exist_ok=True, parents=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Raport complex salvat: {out_path}")