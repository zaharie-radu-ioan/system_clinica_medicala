import json
from pathlib import Path
from app.db import run_select

sql="""
    SELECT
    m.specializare,
    COUNT(c.id_consultatie) AS total_consultatii,
    AVG(c.cost) AS cost_avg,
    SUM(c.cost) AS venit_total
    FROM medic m
    LEFT JOIN programare p ON m.id_medic = p.id_medic
    LEFT JOIN consultatie c ON p.id_programare = c.id_programare
    GROUP BY m.specializare
    ORDER BY total_consultatii DESC;
"""

rows = run_select(sql)

data = []

for row in rows:
    data.append({
        "specializare": row[0],
        "total_consultatii": row[1],
        "cost_mediu": float(row[2]),
        "venit_total": float(row[3]),
    })

out_path = Path("../output") / "statistici_specializari.json"

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON salvat: {out_path}")