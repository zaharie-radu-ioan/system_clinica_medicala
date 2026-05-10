import json
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from app.db import run_select

OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("scripts/logo_clinica.png")

FONT_FAMILY   = "DejaVu Sans"
COLOR_PRIMARY = "#00d4aa"
COLOR_BG      = "#0b1e2d"
COLOR_SURFACE = "#0f2638"
COLOR_GRID    = "#1a3348"
COLOR_TEXT    = "#cce8ff"
COLOR_TEXT2   = "#7aadcc"

plt.rcParams.update({
    "font.family":           FONT_FAMILY,
    "font.size":             11,
    "axes.titlesize":        14,
    "axes.titleweight":      "bold",
    "axes.labelsize":        11,
    "axes.labelcolor":       COLOR_TEXT2,
    "axes.edgecolor":        COLOR_GRID,
    "axes.facecolor":        COLOR_SURFACE,
    "axes.titlecolor":       COLOR_TEXT,
    "figure.facecolor":      COLOR_BG,
    "text.color":            COLOR_TEXT,
    "xtick.color":           COLOR_TEXT2,
    "ytick.color":           COLOR_TEXT2,
    "xtick.labelsize":       10,
    "ytick.labelsize":       10,
    "grid.color":            COLOR_GRID,
    "grid.linewidth":        0.8,
    "grid.linestyle":        "--",
    "legend.facecolor":      COLOR_SURFACE,
    "legend.edgecolor":      COLOR_GRID,
    "legend.labelcolor":     COLOR_TEXT,
    "savefig.facecolor":     COLOR_BG,
    "savefig.edgecolor":     COLOR_BG,
})


def generate_logo(path):
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(3, 3), facecolor="none")
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")

    ring = plt.Circle((0, 0), 1.15, fill=False,
                       edgecolor="#00d4aa", linewidth=2.5, zorder=3)
    ax.add_patch(ring)

    bg = plt.Circle((0, 0), 1.05,
                     facecolor="#0b1e2d", edgecolor="none", zorder=1)
    ax.add_patch(bg)

    cross_v = mpatches.FancyBboxPatch(
        (-0.14, -0.52), 0.28, 1.04,
        boxstyle="round,pad=0.06",
        facecolor="#00d4aa", edgecolor="none", zorder=4
    )
    cross_h = mpatches.FancyBboxPatch(
        (-0.52, -0.14), 1.04, 0.28,
        boxstyle="round,pad=0.06",
        facecolor="#00d4aa", edgecolor="none", zorder=4
    )
    ax.add_patch(cross_v)
    ax.add_patch(cross_h)

    for alpha, scale in [(0.08, 1.6), (0.12, 1.3)]:
        glow_v = mpatches.FancyBboxPatch(
            (-0.14 * scale, -0.52 * scale), 0.28 * scale, 1.04 * scale,
            boxstyle="round,pad=0.08",
            facecolor="#00d4aa", edgecolor="none", alpha=alpha, zorder=3
        )
        glow_h = mpatches.FancyBboxPatch(
            (-0.52 * scale, -0.14 * scale), 1.04 * scale, 0.28 * scale,
            boxstyle="round,pad=0.08",
            facecolor="#00d4aa", edgecolor="none", alpha=alpha, zorder=3
        )
        ax.add_patch(glow_v)
        ax.add_patch(glow_h)

    ax.text(0, -0.82, "ZAH", ha="center", va="center",
            fontfamily=FONT_FAMILY, fontsize=13, fontweight="bold",
            color="#00d4aa", zorder=5)

    ax.plot([-0.38, 0.38], [-0.70, -0.70],
            color="#00d4aa", linewidth=0.8, alpha=0.5, zorder=4)

    plt.savefig(str(path_obj), dpi=300, bbox_inches="tight",
                transparent=True, pad_inches=0.05)
    plt.close()
    print(f"Logo generat: {path_obj}")


def normalize(v):
    if isinstance(v, Decimal):
        x = float(v)
        return int(x) if x.is_integer() else x
    return v


def sanitize_text(text):
    if not isinstance(text, str):
        return str(text)
    replacements = {
        'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't',
        'Ă': 'A', 'Â': 'A', 'Î': 'I', 'Ș': 'S', 'Ț': 'T'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def fetch_data_specializari():
    sql = """
    SELECT m.specializare, COUNT(p.id_programare) as total_pacienti
    FROM medic m
    JOIN programare p ON m.id_medic = p.id_medic
    WHERE p.status = 'finalizata'
    GROUP BY m.specializare
    ORDER BY total_pacienti DESC
    LIMIT 5
    """
    rows = run_select(sql)
    return [{"name": r[0], "value": normalize(r[1])} for r in rows]


def fetch_data_status_programari():
    sql = """
    SELECT status, COUNT(id_programare) as total
    FROM programare
    GROUP BY status
    ORDER BY total DESC
    """
    rows = run_select(sql)
    return [{"name": r[0].capitalize(), "value": normalize(r[1])} for r in rows]


def export_csv(data, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "value"])
        writer.writeheader()
        writer.writerows(data)


def export_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_bar_chart(data, file_path, title, xlabel, ylabel):
    names  = [sanitize_text(d["name"]) for d in data]
    values = [d["value"] for d in data]
    n      = len(names)
    x      = np.arange(n)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.18)

    bar_colors = [
        plt.matplotlib.colors.to_rgba(COLOR_PRIMARY, alpha=0.55 + 0.45 * (i / max(n - 1, 1)))
        for i in range(n)
    ]

    bars = ax.bar(x, values, color=bar_colors,
                  edgecolor=COLOR_PRIMARY, linewidth=0.8,
                  width=0.55, zorder=3)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(values) * 0.015,
                str(val), ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=COLOR_TEXT)

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20, ha="right")
    ax.set_xlabel(sanitize_text(xlabel), labelpad=8)
    ax.set_ylabel(sanitize_text(ylabel), labelpad=8)
    ax.set_title(sanitize_text(title), pad=16)

    ax.yaxis.grid(True, zorder=0)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(COLOR_GRID)

    plt.savefig(str(file_path), dpi=150)
    plt.close()


def generate_pie_chart(data, file_path, title):
    names  = [sanitize_text(d["name"]) for d in data]
    values = [d["value"] for d in data]

    palette = {
        "Finalizata": "#00d4aa",
        "Anulata":    "#f16f6f",
        "Programata": "#4f9cf9",
    }
    pie_colors = [palette.get(n, "#7aadcc") for n in names]

    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    fig.subplots_adjust(left=0.0, right=0.78, top=0.88, bottom=0.08)

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        autopct="%1.1f%%",
        startangle=140,
        colors=pie_colors,
        pctdistance=0.72,
        wedgeprops={"edgecolor": COLOR_BG, "linewidth": 2},
        shadow=False,
    )

    for at in autotexts:
        at.set(fontsize=10, fontweight="bold", color="#0b1e2d")

    legend_labels = [f"{n}  ({v:,})" for n, v in zip(names, values)]
    ax.legend(wedges, legend_labels,
              loc="center left", bbox_to_anchor=(1.02, 0.5),
              framealpha=0, fontsize=10)

    ax.set_title(sanitize_text(title), pad=16)
    plt.savefig(str(file_path), dpi=150)
    plt.close()


def generate_pdf(data, pdf_path, chart_path, title, description, col_names):
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=20,
        textColor=colors.HexColor("#004080")
    )
    normal_style = styles["Normal"]

    if LOGO_PATH.exists():
        logo = Image(str(LOGO_PATH), width=1.0 * inch, height=1.0 * inch)
        elements.append(logo)
        elements.append(Spacer(1, 20))

    elements.append(Paragraph(sanitize_text("Raport Activitate Medicala - BI"), title_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(sanitize_text(title), styles["Heading2"]))
    elements.append(Spacer(1, 15))

    intro_text = (
        f"{sanitize_text(description)}<br/>"
        f"Raport generat la data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 20))

    table_data = [[sanitize_text(col_names[0]), sanitize_text(col_names[1])]]
    for d in data:
        table_data.append([sanitize_text(d["name"]), sanitize_text(str(d["value"]))])

    table = Table(table_data, colWidths=[250, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor("#0073e6")),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE',      (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  10),
        ('BACKGROUND',    (0, 1), (-1, -1), colors.HexColor("#f2f8ff")),
        ('GRID',          (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 25))

    if Path(chart_path).exists():
        chart = Image(str(chart_path), width=6 * inch, height=4 * inch)
        elements.append(chart)

    doc.build(elements)


def main():
    print("Incepe generarea rapoartelor de Business Intelligence...\n")

    generate_logo(LOGO_PATH)

    data_spec = fetch_data_specializari()
    if data_spec:
        export_csv(data_spec, OUT_DIR / "Top_Specializari.csv")
        export_json(data_spec, OUT_DIR / "Top_Specializari.json")
        generate_bar_chart(
            data_spec,
            OUT_DIR / "Specializari_Chart.png",
            "Top 5 Cele Mai Solicitate Specializari",
            "Specializare",
            "Numar Consultatii"
        )
        generate_pdf(
            data_spec,
            OUT_DIR / "Raport_Specializari.pdf",
            OUT_DIR / "Specializari_Chart.png",
            "Top 5 Specializari Medicale",
            "Acest raport analizeaza volumul de consultatii finalizate pentru cele mai solicitate ramuri medicale. Datele reflecta distributia pacientilor si incarcarea medicilor pe sectii, permitand alocarea optima a resurselor umane in cadrul clinicii.",
            ["Specializare Medicala", "Nr. Programari"]
        )
        print("Raportul 'Top Specializari' a fost generat.")
    else:
        print("Nu exista date pentru raportul 'Top Specializari'.")

    data_status = fetch_data_status_programari()
    if data_status:
        export_csv(data_status, OUT_DIR / "Status_Programari.csv")
        export_json(data_status, OUT_DIR / "Status_Programari.json")
        generate_pie_chart(
            data_status,
            OUT_DIR / "Status_Chart.png",
            "Rata de Onorare a Programarilor"
        )
        generate_pdf(
            data_status,
            OUT_DIR / "Raport_Status_Programari.pdf",
            OUT_DIR / "Status_Chart.png",
            "Statistica Programari (Finalizate vs. Anulate)",
            "Acest raport detaliat ofera o imagine de ansamblu asupra eficientei operationale a clinicii medicale. Prin analiza statusului programarilor, conducerea poate evalua cu precizie rata de onorare a consultatiilor, impactul negativ al anularilor asupra fluxului financiar si numarul de programari aflate inca in asteptare. Aceste informatii sunt vitale pentru optimizarea timpului alocat de medici si pentru implementarea unor politici eficiente de reducere a programarilor neprezentate.",
            ["Status Programare", "Total Pachet"]
        )
        print("Raportul 'Status Programari' a fost generat.")
    else:
        print("Nu exista date pentru raportul 'Status Programari'.")

    print(f"\nToate fisierele au fost salvate in folderul: {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()