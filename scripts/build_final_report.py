#!/usr/bin/env python3
"""Build the polished DOCX submission from verified project outputs."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "report"
FIG_DIR = REPORT_DIR / "figures"
OUTPUT = REPORT_DIR / "BigDataSystems_Assignment2_Final_Report.docx"
METRICS = json.loads((ROOT / "output" / "metrics.json").read_text(encoding="utf-8"))

NAVY = "17365D"
BLUE = "1F4E79"
PALE_BLUE = "D9EAF7"
LIGHT = "F3F6F9"
GRAY = "5B6573"
ORANGE = "C55A11"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text, *, bold=False, color=None, size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(str(text))
    run.bold = bold
    run.font.name = "Aptos"
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def set_cell_margins(cell, top=90, start=100, bottom=90, end=100):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for m, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn("w:" + m))
        if node is None:
            node = OxmlElement("w:" + m)
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def add_table(doc, headers, rows, widths=None, font_size=8.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    header = table.rows[0]
    set_repeat_table_header(header)
    for i, label in enumerate(headers):
        set_cell_text(header.cells[i], label, bold=True, color="FFFFFF", size=font_size)
        shade(header.cells[i], NAVY)
        set_cell_margins(header.cells[i])
    for ridx, values in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(values):
            set_cell_text(cells[i], value, size=font_size)
            set_cell_margins(cells[i])
            if ridx % 2 == 1:
                shade(cells[i], LIGHT)
    if widths:
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = Inches(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_field(paragraph, instruction):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for element in (begin, instr, separate, text, end):
        run._r.append(element)


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor.from_string(GRAY)


def add_body(doc, text, *, bold_lead=None):
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.08
    if bold_lead and text.startswith(bold_lead):
        p.add_run(bold_lead).bold = True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    p.add_run(text)
    return p


def add_code(doc, text):
    for line in text.strip("\n").splitlines():
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.16)
        p.paragraph_format.right_indent = Inches(0.12)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.keep_together = True
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "F1F3F5")
        pPr.append(shd)
        run = p.add_run(line if line else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor.from_string("20252B")


def add_figure(doc, filename, caption, width=6.2):
    path = FIG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(path)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    add_caption(doc, caption)


def add_screenshot_placeholder(doc, title, instruction, height=2.2):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.2)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    shade(cell, "F8FAFC")
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(20)
    r = p.add_run("[SCREENSHOT TO ADD]\n")
    r.bold = True
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor.from_string(ORANGE)
    r2 = p.add_run(title + "\n" + instruction)
    r2.font.size = Pt(9)
    r2.font.color.rgb = RGBColor.from_string(GRAY)
    table.rows[0].height = Inches(height)
    add_caption(doc, title)


def make_architecture_diagram(path):
    fig, ax = plt.subplots(figsize=(11, 4.7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")

    def box(x, y, w, h, title, detail, color):
        rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor="#18324F",
                             linewidth=1.5, joinstyle="round")
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center",
                fontsize=11, weight="bold", color="#17365D")
        ax.text(x + w / 2, y + h * 0.31, detail, ha="center", va="center",
                fontsize=8.5, color="#263746", wrap=True)

    def arrow(x1, y1, x2, y2, label=None):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops={"arrowstyle": "->", "lw": 1.8, "color": "#50677E"})
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.16, label,
                    ha="center", fontsize=8, color="#40566C")

    box(0.2, 1.55, 2.0, 1.65, "UCI CSV", "101,766 encounters\npublic clinical dataset", "#EAF2F8")
    box(2.8, 1.55, 2.1, 1.65, "Python ETL", "Normalize documents\nseed synthetic fields", "#E8F3EC")
    box(5.5, 1.55, 2.2, 1.65, "MongoDB · VM1", "patients · encounters\nvitals · predictions", "#FFF2CC")
    box(8.5, 3.25, 2.2, 1.35, "Mongo analytics", "$lookup · $graphLookup\n$setWindowFields · $bucket", "#EAF2F8")
    box(8.5, 0.45, 2.2, 1.45, "Spark · 2 VMs", "MLlib RF / GBT\npatient-held-out scoring", "#FCE4D6")
    arrow(2.2, 2.38, 2.8, 2.38, "prepare")
    arrow(4.9, 2.38, 5.5, 2.38, "JSONL load")
    arrow(7.7, 2.65, 8.5, 3.65, "aggregation")
    arrow(7.7, 2.0, 8.5, 1.2, "Mongo connector")
    arrow(8.5, 0.75, 7.7, 1.65, "write predictions")
    ax.text(5.5, 4.35, "Hybrid document analytics and distributed ML architecture",
            ha="center", fontsize=15, weight="bold", color="#17365D")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def configure_document(doc):
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)
    section.header_distance = Inches(0.32)
    section.footer_distance = Inches(0.32)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = RGBColor.from_string("263238")
    normal.paragraph_format.space_after = Pt(5)
    for style_name, size in (("Title", 27), ("Heading 1", 17), ("Heading 2", 12), ("Heading 3", 10)):
        style = styles[style_name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(NAVY if style_name != "Title" else BLUE)
        style.paragraph_format.keep_with_next = True
    styles["Heading 1"].paragraph_format.space_before = Pt(14)
    styles["Heading 1"].paragraph_format.space_after = Pt(7)
    styles["Heading 2"].paragraph_format.space_before = Pt(9)
    styles["Heading 2"].paragraph_format.space_after = Pt(4)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run("CC ZG522  |  Big Data Systems  |  Assignment 2")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string(GRAY)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f = footer.add_run("Dhruv Kumar  ·  2026NS03024     |     Page ")
    f.font.size = Pt(8)
    f.font.color.rgb = RGBColor.from_string(GRAY)
    add_field(footer, "PAGE")


def build():
    doc = Document()
    configure_document(doc)
    doc.core_properties.title = "Big Data Systems Assignment 2 — Healthcare Readmission Analytics"
    doc.core_properties.subject = "MongoDB and Apache Spark hybrid analytics"
    doc.core_properties.author = "Dhruv Kumar"
    doc.core_properties.keywords = "MongoDB, Apache Spark, MLlib, readmission, Big Data"

    # Cover
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(46)
    r = p.add_run("BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE, PILANI")
    r.bold = True
    r.font.size = Pt(15)
    r.font.color.rgb = RGBColor.from_string(NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Work Integrated Learning Programmes Division").font.size = Pt(11)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(34)
    r = p.add_run("BIG DATA SYSTEMS")
    r.bold = True
    r.font.size = Pt(17)
    r.font.color.rgb = RGBColor.from_string(BLUE)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    r = p.add_run("Assignment 2")
    r.bold = True
    r.font.size = Pt(29)
    r.font.color.rgb = RGBColor.from_string(NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Healthcare Readmission Analytics\nA Hybrid MongoDB and Apache Spark Implementation")
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor.from_string(GRAY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(30)
    p.add_run("Scenario 3 · Track C · Self-hosted two-VM cluster").bold = True
    doc.add_paragraph()
    add_table(doc, ["Submission detail", "Information"], [
        ("Student", "Dhruv Kumar"),
        ("BITS ID", "2026NS03024"),
        ("Course", "CC ZG522 — Big Data Systems"),
        ("Instructor", "Dr D. Venkata Subramanian"),
        ("Semester", "First Semester 2026–2027"),
        ("Submission date", "1 November 2026"),
    ], widths=[2.0, 4.2], font_size=10)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    p.add_run("Work Integrated Learning Programmes Division").italic = True
    doc.add_page_break()

    doc.add_heading("Executive Summary", level=1)
    add_body(doc, "This project implements a hybrid big-data workflow for 30-day hospital readmission analysis. The UCI Diabetes 130-US Hospitals dataset was normalized into patient, encounter, and vital-sign documents in MongoDB. MongoDB aggregation pipelines demonstrate demographic joins, synthetic patient-history traversal, rolling vital statistics, and length-of-stay summaries. Apache Spark MLlib reads encounter and patient data through the MongoDB Spark Connector, trains Random Forest and Gradient-Boosted Tree classifiers, evaluates them on a patient-held-out test set, and writes test predictions back to MongoDB.")
    add_body(doc, "The data contains 101,766 encounters, 71,518 patients, and 814,128 synthetic vital records. Only 11.16% of encounters are labeled as readmitted within 30 days. A leakage audit found that the synthetic vital generator uses the target label; these fields were therefore excluded from model training. The final patient-level holdout contains 20,642 encounters. Random Forest achieved AUROC 0.6315 and recall 0.0834 at the default threshold; GBT achieved AUROC 0.6275 and recall 0.1545. Both are weak models and both default-threshold accuracies are below the 88.55% majority-class baseline. They are educational demonstrations, not suitable for clinical use.")
    add_body(doc, "The implementation validates the end-to-end MongoDB–Spark integration and provides reproducible scripts, aggregate outputs, and visualizations. It does not claim a runtime speedup, causal associations, calibrated probabilities, or clinical validity.")
    doc.add_heading("Contents", level=1)
    contents = [
        "1. Problem statement and objectives",
        "2. Theoretical foundation",
        "3. Data source and Big Data lifecycle",
        "4. Architecture, environment, and technology stack",
        "5. Implementation and reproducibility",
        "6. Verified analytical results",
        "7. Model evaluation and interpretation",
        "8. Visualizations and insights",
        "9. Limitations, conclusion, and future work",
        "Remote repository",
        "Appendices: commands, re-query examples, and screenshot placeholders",
    ]
    for item in contents:
        add_bullet(doc, item)
    doc.add_page_break()

    # 1. Problem
    doc.add_heading("1. Problem Statement and Objectives", level=1)
    doc.add_heading("1.1 Context", level=2)
    add_body(doc, "Hospital readmission is an important operational and care-quality outcome. The assignment scenario concerns combining electronic health records, demographic information, longitudinal measurements, and clinical context to estimate whether a patient will return within 30 days. This implementation uses the UCI diabetes encounters dataset as a public proxy; it does not contain real wearable streams or continuous glucose monitoring.")
    doc.add_heading("1.2 Problem formulation", level=2)
    add_body(doc, "For each encounter, classify the binary target y = 1 when the source readmission label is <30 and y = 0 for NO or >30. The encounter is the prediction row, but evaluation is grouped by patient so that a patient's records do not occur in both training and test partitions.")
    doc.add_heading("1.3 Objectives", level=2)
    for item in [
        "Model patient and encounter records as related MongoDB document collections.",
        "Demonstrate MongoDB $lookup, $graphLookup, $setWindowFields, and $bucket.",
        "Use a two-node Spark standalone cluster for distributed feature processing and MLlib training.",
        "Write held-out prediction scores to MongoDB and validate their row count.",
        "Evaluate results honestly, account for class imbalance, and document synthetic-data leakage.",
    ]:
        add_bullet(doc, item)

    # 2. Theory
    doc.add_heading("2. Theoretical Foundation", level=1)
    doc.add_heading("2.1 Document databases and aggregation", level=2)
    add_body(doc, "MongoDB stores flexible BSON documents and supports aggregation pipelines that move filtering, joining, grouping, and window computation near the data. $lookup performs a left outer join against another collection; $graphLookup recursively follows matching keys; $setWindowFields computes ordered partition windows; and $bucket categorizes numeric values into explicit intervals.")
    doc.add_heading("2.2 Distributed processing with Spark", level=2)
    add_body(doc, "Apache Spark represents distributed data as DataFrames and plans transformations for parallel execution. A standalone master allocates worker resources; the driver coordinates jobs, while executors run tasks. The MongoDB Spark Connector provides source and sink integrations so large collections need not be exported into ad hoc local files.")
    doc.add_heading("2.3 Classification and evaluation", level=2)
    add_body(doc, "Random Forest aggregates many decision trees; Gradient-Boosted Trees sequentially add trees to reduce residual errors. AUROC measures ranking across thresholds; AUPR summarizes the precision–recall curve and is informative under imbalance. At a fixed threshold, accuracy = (TP + TN) / N, precision = TP / (TP + FP), recall = TP / (TP + FN), and F1 is the harmonic mean of precision and recall. A majority-class baseline is essential because accuracy can appear high even when a model misses positives.")
    doc.add_heading("2.4 Leakage and evaluation design", level=2)
    add_body(doc, "Target leakage occurs when a feature contains information derived from the label or from events unavailable at prediction time. Here synthetic vitals are generated with a class-dependent shift using the readmission target, so using those values as model inputs would directly leak outcome information. Patient-level splitting also avoids identity/history overlap between train and test. Both safeguards are used in the final run.")

    # 3. Data and lifecycle
    doc.add_heading("3. Data Source and Big Data Lifecycle", level=1)
    doc.add_heading("3.1 Dataset", level=2)
    add_body(doc, "The source is the UCI Diabetes 130-US hospitals dataset (1999–2008). It contains encounter-level utilization, diagnoses, laboratory, medication, demographic, and readmission data. The loaded dataset contains 101,766 encounters linked to 71,518 unique patients. Original readmission labels are NO, >30, and <30; the project maps only <30 to the positive class.")
    add_body(doc, "Synthetic enrichment adds patient-linked timestamps, previous-encounter pointers, templated notes, and eight three-hourly heart-rate/glucose observations per encounter. Synthetic time and vital data are useful for demonstrating data modeling and operators, but are not observed clinical measurements and are not model features.")
    doc.add_heading("3.2 Lifecycle followed", level=2)
    add_table(doc, ["Lifecycle stage", "Project activity", "Output / control"], [
        ("1. Business understanding", "Define binary 30-day readmission question and hybrid compute objective.", "Explicit target: <30 vs other source labels."),
        ("2. Data acquisition", "Download official UCI dataset; verify archive and extract source CSV.", "Reproducible public input."),
        ("3. Preparation", "Normalize patient/encounter documents; nest diagnoses/medications; create seeded synthetic fields.", "JSONL for three collections; deterministic seed."),
        ("4. Ingestion and storage", "Bulk-load MongoDB; create unique and query indexes.", "71,518 patients; 101,766 encounters; 814,128 vitals."),
        ("5. Processing", "Run Mongo aggregation pipelines and Spark joins/features/models.", "Mongo analytics and distributed ML outputs."),
        ("6. Evaluation", "Patient-hash holdout; compare RF/GBT, confusion matrices, and majority baseline.", "20,642 unseen encounters; leakage-safe features."),
        ("7. Serving / persistence", "Write held-out predictions to MongoDB.", "20,642 unique prediction documents."),
        ("8. Communication", "Generate charts and this report; reserve spaces for runtime screenshots.", "DOCX submission, figures, reproducible queries."),
    ], widths=[1.25, 3.0, 2.05], font_size=8)

    # 4. Architecture and stack
    doc.add_heading("4. Architecture, Environment, and Technology Stack", level=1)
    add_figure(doc, "architecture.png", "Figure 1. Hybrid data flow from UCI source through MongoDB and Spark to analytical outputs.", width=6.55)
    doc.add_heading("4.1 Execution environment", level=2)
    add_table(doc, ["Component", "Verified configuration"], [
        ("Operating system", "Rocky Linux 10.2 on both VMs"),
        ("Runtime", "Java 21; Python 3.12"),
        ("Distributed processing", "Apache Spark 4.1.2 standalone; one master/driver VM and one worker VM"),
        ("Document store", "MongoDB 7.0.14; mongosh 2.5.6 on driver VM"),
        ("Private service network", "Driver/Mongo/Spark master 192.168.224.241; worker 192.168.224.240"),
        ("Connector", "MongoDB Spark Connector 11.1.0; MongoDB Java driver/BSON 5.1.4"),
        ("Libraries", "PySpark MLlib, pandas, PyMongo, matplotlib"),
    ], widths=[2.0, 4.2], font_size=8.5)
    doc.add_heading("4.2 Tools and responsibilities", level=2)
    add_table(doc, ["Technology/tool", "Use"], [
        ("MongoDB", "Operational document collections and aggregation analytics."),
        ("Apache Spark / PySpark", "Distributed DataFrame preparation and MLlib classifiers."),
        ("MongoDB Spark Connector", "Read Mongo collections and write predictions."),
        ("Python", "ETL, orchestration, evaluation, and figure generation."),
        ("mongosh", "Interactive validation and screenshot-friendly aggregation queries."),
        ("Git / shell scripts", "Repeatable setup, dependency handling, and run commands."),
    ], widths=[2.0, 4.2], font_size=8.5)
    doc.add_heading("4.3 Runtime evidence (to be inserted)", level=2)
    add_screenshot_placeholder(doc, "Spark standalone cluster", "Insert Spark master UI showing the worker in ALIVE state.", 1.45)

    # 5. Implementation
    doc.add_heading("5. Implementation and Reproducibility", level=1)
    doc.add_heading("5.1 MongoDB data model", level=2)
    add_table(doc, ["Collection", "Key fields / purpose", "Document count"], [
        ("patients", "patient_nbr, race, gender, age", "71,518"),
        ("encounters", "encounter_id, patient_nbr, diagnoses[], medications[], labels, utilization", "101,766"),
        ("vitals", "encounter_id, timestamp, heart_rate_bpm, glucose_mg_dl", "814,128"),
        ("predictions", "encounter_id, label, probability, prediction, model", "20,642"),
    ], widths=[1.15, 4.05, 1.0], font_size=8)
    add_body(doc, "Indexes include unique patient_nbr and encounter_id keys, encounter patient/readmission/previous-encounter indexes, and a compound (encounter_id, ts) vitals index. Integrity checks found no encounter without a matching patient, no duplicate encounter identifiers, and exactly eight vital records for every encounter.")
    doc.add_heading("5.2 MongoDB analytical operations", level=2)
    add_table(doc, ["Operator", "Purpose", "Verified output"], [
        ("$lookup", "Join encounters to patient demographics and summarize readmission counts/rates by race.", "All encounters join; race groups and counts reported in Section 6."),
        ("$graphLookup", "Follow synthetic prev_encounter_id links, depth-capped at maxDepth 5.", "First 500 eligible roots: mean 1.498 linked stays; maximum 6."),
        ("$setWindowFields", "Three-observation trailing mean of heart rate per encounter.", "Encounter 12522 first means: 83.50, 84.05, 84.27 bpm."),
        ("$bucket", "Count encounters and <30 outcomes by LOS intervals.", "Four non-empty buckets: 1–3, 4–7, 8–11, 12–15 days."),
    ], widths=[1.3, 3.2, 1.7], font_size=8)
    add_screenshot_placeholder(doc, "MongoDB query result", "Insert mongosh output showing collection counts or an aggregation result.", 1.35)
    doc.add_heading("5.3 Spark model workflow", level=2)
    for item in [
        "Read encounters and join patient demographics by patient_nbr.",
        "Cast numeric fields and handle missing categorical values; index gender, age, A1Cresult, diabetesMed, and insulin.",
        "Exclude synthetic vitals and templated notes to avoid leakage.",
        "Partition by stable patient hash (80/20 using seed 42); verify there is no patient overlap.",
        "Downsample only the training majority class to approximately twice the positive count.",
        "Fit Random Forest (80 trees) and GBT (40 iterations); evaluate on the natural-prevalence holdout.",
        "Select the higher-AUROC model and write one prediction for every held-out encounter.",
    ]:
        add_bullet(doc, item)
    add_screenshot_placeholder(doc, "Spark distributed execution", "Insert Spark UI stages or terminal evidence showing tasks on the worker VM.", 1.35)

    # 6. Findings
    doc.add_heading("6. Verified Analytical Results", level=1)
    doc.add_heading("6.1 Dataset and label integrity", level=2)
    add_table(doc, ["Readmission label", "Encounters", "Share"], [
        ("NO", "54,864", "53.91%"),
        (">30", "35,545", "34.93%"),
        ("<30 (positive)", "11,357", "11.16%"),
        ("Total", "101,766", "100.00%"),
    ], widths=[2.3, 1.8, 1.2], font_size=9)
    add_figure(doc, "fig1_readmission_counts.png", "Figure 2. Distribution of source readmission labels.", width=5.8)
    doc.add_heading("6.2 Readmission rates by race", level=2)
    add_table(doc, ["Race", "Encounters", "<30 events", "Rate"], [
        ("Caucasian", "76,043", "8,581", "11.28%"),
        ("African American", "19,165", "2,154", "11.24%"),
        ("Unknown / missing", "2,367", "204", "8.62%"),
        ("Hispanic", "2,063", "217", "10.52%"),
        ("Other", "1,517", "141", "9.29%"),
        ("Asian", "611", "60", "9.82%"),
    ], widths=[2.0, 1.3, 1.2, 1.0], font_size=8.5)
    add_body(doc, "These unadjusted descriptive rates are not causal or risk-adjusted comparisons. Smaller race groups have relatively few encounters.")
    doc.add_heading("6.3 Readmission rates by length of stay", level=2)
    add_table(doc, ["Length-of-stay bucket", "Encounters", "<30 events", "Rate"], [
        ("1–3 days", "49,188", "4,768", "9.69%"),
        ("4–7 days", "37,288", "4,544", "12.19%"),
        ("8–11 days", "11,590", "1,568", "13.53%"),
        ("12–15 days", "3,700", "477", "12.89%"),
    ], widths=[2.0, 1.3, 1.2, 1.0], font_size=8.5)
    add_figure(doc, "fig3_los_readmission.png", "Figure 3. Thirty-day readmission rate by LOS; zero-based vertical axis.", width=5.8)
    add_body(doc, "The observed rate rises through the 8–11 day group and is lower in the 12–15 day group. No 16+ day bucket was present. This pattern is descriptive and does not establish that LOS causes readmission.")
    doc.add_heading("6.4 Readmission by age bracket", level=2)
    add_body(doc, "Age is joined from the patient collection. The figure omits brackets with fewer than 500 encounters; labels show both rates and sample sizes. The pattern is non-monotonic: the [20–30) bracket has 13.84% (233/1,683), while [50–60) has 9.65% (1,679/17,393). The [0–10) group has 1.84% (3/163) and is omitted by the display threshold.")
    add_figure(doc, "fig2_readmission_by_age.png", "Figure 4. Unadjusted readmission rate by UCI age bracket; age joined from patients.", width=6.25)
    doc.add_heading("6.5 Synthetic vital and graph demonstrations", level=2)
    add_body(doc, "The 500-root graph traversal returned an average 1.498 linked prior stays and maximum 6 with maxDepth 5. The rolling-window example uses the current and prior two three-hourly readings. The plotted heart-rate series is synthetic and target-dependent, and therefore only demonstrates time-series storage/windowing—not clinical discovery or model utility.")
    add_figure(doc, "fig4_vitals_series.png", "Figure 5. Synthetic heart-rate sequence for encounter 24437208; values are not model features.", width=6.0)

    # 7. Model
    doc.add_heading("7. Model Evaluation and Interpretation", level=1)
    add_body(doc, "The deterministic patient hash split held out 14,440 patients / 20,642 encounters and assigned 57,078 patients to the training partition. After majority downsampling, model fitting used 26,944 encounters from 21,437 patients (8,994 positives; 17,950 negatives). The test set retained natural class prevalence: 2,363 positives (11.45%) and 18,279 negatives. The majority-class accuracy baseline is 88.55%.")
    add_table(doc, ["Model", "AUROC", "AUPR", "Accuracy", "Precision", "Recall", "F1"], [
        ("Random Forest", "0.6315", "0.1987", "0.8756", "0.3294", "0.0834", "0.1331"),
        ("GBT", "0.6275", "0.1948", "0.8524", "0.2581", "0.1545", "0.1933"),
        ("Majority baseline", "—", "—", "0.8855", "—", "0", "0"),
    ], widths=[1.35, .75, .75, .85, .85, .75, .55], font_size=8)
    add_figure(doc, "fig5_model_metrics.png", "Figure 6. Patient-held-out AUROC and AUPR from the final leakage-controlled run.", width=5.8)
    doc.add_heading("7.1 Confusion matrices at threshold 0.5", level=2)
    add_table(doc, ["Model", "TP", "TN", "FP", "FN", "Specificity"], [
        ("Random Forest", "197", "17,878", "401", "2,166", "0.9781"),
        ("GBT", "365", "17,230", "1,049", "1,998", "0.9426"),
    ], widths=[1.7, .7, 1.0, .8, .8, 1.0], font_size=8.5)
    add_body(doc, "Random Forest was selected by AUROC and wrote the held-out predictions. Both AUROCs are modestly above chance and AUPRs exceed test prevalence, but neither model beats the majority-class accuracy baseline at threshold 0.5. Random Forest recall is only 8.34%; GBT recall is 15.45%. The models miss many positive cases. Probabilities are not calibrated after training downsampling. These results are not ready for clinical or operational decision-making.")

    # 8. Discussion
    doc.add_heading("8. Big Data Insights and Compute Placement", level=1)
    for item in [
        "Data modeling matters: demographics reside in one patient document per patient and are joined to encounters using indexed identifiers.",
        "MongoDB aggregation is effective for colocated descriptive joins, bucket summaries, recursive links, and per-encounter windows; reported outputs are reproducible from the provided scripts.",
        "Spark successfully performed distributed ETL/model tasks on the worker and returned test predictions to MongoDB. This validates integration, not a measured speedup.",
        "The original synthetic vitals intentionally vary by outcome and would make an invalid predictive feature. Excluding them materially reduced headline metrics and prevented target leakage.",
        "A patient-level holdout is stricter than a random encounter split because repeat encounters from the same person cannot leak across partitions.",
        "Class imbalance makes accuracy alone misleading. The majority baseline and recall expose the models' weak positive-case detection.",
    ]:
        add_bullet(doc, item)

    # 9. Limits and conclusion
    doc.add_heading("9. Limitations, Conclusion, and Future Work", level=1)
    doc.add_heading("9.1 Limitations", level=2)
    for item in [
        "The source dataset is historical (1999–2008), diabetes-focused, and uses ICD-9-era fields rather than a modern complete EHR.",
        "Admission timestamps, prior-stay links, and vital streams are synthetic; their distributions should not be treated as real clinical evidence.",
        "The current model has weak recall and does not outperform a majority accuracy baseline; no threshold tuning, calibration, cross-validation, subgroup fairness analysis, or external/temporal validation was performed.",
        "The assignment did not benchmark MongoDB against Spark or quantify throughput, latency, or scale-up performance.",
        "Screenshots of the live cluster and runtime still need to be inserted before submission.",
    ]:
        add_bullet(doc, item)
    doc.add_heading("9.2 Conclusion", level=2)
    add_body(doc, "The project delivers a reproducible hybrid MongoDB–Spark workflow aligned with the assignment's Track C objectives: document modeling, aggregation analytics, distributed MLlib execution, and prediction persistence. The analysis surfaces meaningful methodological lessons—particularly target leakage, patient-level evaluation, and imbalanced metrics. The final classifier is a pipeline demonstration rather than a validated readmission-risk solution.")
    doc.add_heading("9.3 Future work", level=2)
    add_body(doc, "Future extensions should use genuine time-stamped clinical data, define prediction-time feature availability, add patient-level cross-validation and temporal testing, calibrate probabilities, select thresholds according to clinical utility, evaluate subgroup performance, and compare MongoDB and Spark runtimes under controlled workloads.")

    # Repository page directly before appendix
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(110)
    r = p.add_run("PROJECT REPOSITORY")
    r.bold = True
    r.font.size = Pt(23)
    r.font.color.rgb = RGBColor.from_string(NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    r = p.add_run("BigDataAssignment2")
    r.bold = True
    r.font.size = Pt(17)
    repo = "https://github.com/2026ns03024-eng/BigDataAssignment2"
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    run = p.add_run(repo)
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor.from_string(BLUE)
    run.underline = True
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(22)
    p.add_run("Source code, runbooks, query scripts, report figures, and reproducibility instructions.").font.size = Pt(10)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(16)
    r = p.add_run("Repository access may require GitHub authentication.")
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor.from_string(GRAY)

    # Appendices
    doc.add_page_break()
    doc.add_heading("Appendix A — Reproduction Commands and MongoDB Queries", level=1)
    add_body(doc, "Run commands from the repository root on the driver VM after configuring config.env and starting MongoDB/Spark. The examples below reproduce the reported summaries; all database queries are read-only.")
    doc.add_heading("A.1 Environment and collection counts", level=2)
    add_code(doc, """source scripts/source_cluster_env.sh
set -a
source config.env
set +a
mongosh "mongodb://${MONGO_HOST}:${MONGO_PORT}/${MONGO_DB}" --quiet --eval '
  printjson({
    patients: db.patients.countDocuments(),
    encounters: db.encounters.countDocuments(),
    vitals: db.vitals.countDocuments(),
    predictions: db.predictions.countDocuments()
  })
'""")
    add_body(doc, "Verified before finalization: 71,518 patients; 101,766 encounters; 814,128 vitals; and 20,642 unique predictions.")

    doc.add_heading("A.2 Target-label distribution", level=2)
    add_code(doc, """db.encounters.aggregate([
  {$group: {_id: "$readmitted", n: {$sum: 1}}},
  {$sort: {_id: 1}}
])""")
    add_body(doc, "Expected rows: <30 = 11,357; >30 = 35,545; NO = 54,864. The derived target is 1 only when readmitted equals <30.")

    doc.add_heading("A.3 LOS bucket query", level=2)
    add_code(doc, """db.encounters.aggregate([
  {$addFields: {positive: {$cond: [{$eq: ["$readmitted", "<30"]}, 1, 0]}}},
  {$bucket: {
    groupBy: "$time_in_hospital",
    boundaries: [1, 4, 8, 12, 16],
    default: "16+",
    output: {
      encounters: {$sum: 1},
      readmit_30d: {$sum: "$positive"}
    }
  }},
  {$addFields: {
    rate: {$round: [{$divide: ["$readmit_30d", "$encounters"]}, 4]}
  }},
  {$sort: {_id: 1}}
])""")
    add_body(doc, "Expected counts/rates: 1–3 days 49,188 / 4,768 / 0.0969; 4–7 days 37,288 / 4,544 / 0.1219; 8–11 days 11,590 / 1,568 / 0.1353; 12–15 days 3,700 / 477 / 0.1289.")

    doc.add_heading("A.4 Age join and rate query", level=2)
    add_code(doc, """db.encounters.aggregate([
  {$lookup: {
    from: "patients", localField: "patient_nbr",
    foreignField: "patient_nbr", as: "patient"
  }},
  {$unwind: "$patient"},
  {$group: {
    _id: "$patient.age",
    encounters: {$sum: 1},
    positives: {$sum: {$cond: [{$eq: ["$readmitted", "<30"]}, 1, 0]}}
  }},
  {$project: {
    encounters: 1, positives: 1,
    rate: {$divide: ["$positives", "$encounters"]}
  }},
  {$sort: {_id: 1}}
])""")
    add_body(doc, "Figure 4 displays only brackets with n >= 500. For example, [20–30) has 233/1,683 = 13.84%; [0–10) has 3/163 = 1.84% and is omitted from the chart.")

    doc.add_heading("A.5 Re-run all MongoDB pipelines", level=2)
    add_code(doc, """python3 scripts/mongo_analytics.py
# Or run operator examples in mongosh:
mongosh "mongodb://${MONGO_HOST}:${MONGO_PORT}/${MONGO_DB}" \\
  --file queries/analytics.js""")
    add_body(doc, "The Python summary normalizes missing race values to Unknown, sorts the 500-root graph sample deterministically, and reports aggregate rates. The JavaScript file provides interactive operator examples.")

    doc.add_heading("A.6 Re-run training and charts", level=2)
    add_code(doc, """set -o pipefail
bash scripts/run_spark_train.sh 2>&1 | tee output/spark_train.log
python3 scripts/make_charts.py""")
    add_body(doc, "The final run's metrics are stored in output/metrics.json. The script checks executor NumPy availability, excludes synthetic vitals, uses a deterministic patient-hash holdout, trains RF/GBT, and overwrites the prediction collection with held-out rows.")

    doc.add_heading("Appendix B — Screenshot Placeholders", level=1)
    add_body(doc, "Replace each outlined box with a genuine capture from the running environment. Do not represent generated diagrams or charts as screenshots.")
    add_screenshot_placeholder(doc, "B.1 Spark cluster topology", "Capture the master UI with the worker hostname, ALIVE state, and resources visible.", 2.3)
    add_screenshot_placeholder(doc, "B.2 MongoDB data and aggregation", "Capture mongosh collection counts or the LOS / $graphLookup result.", 2.3)
    add_screenshot_placeholder(doc, "B.3 Distributed Spark execution", "Capture Spark stages or terminal output showing task execution on the worker.", 2.3)

    doc.add_heading("Appendix C — Metric Definitions and Output Files", level=1)
    add_table(doc, ["Metric", "Definition / interpretation"], [
        ("AUROC", "Area under ROC; ranking discrimination across thresholds; 0.5 is chance."),
        ("AUPR", "Area under precision–recall curve; compare with positive prevalence (11.45%)."),
        ("Precision", "TP / (TP + FP); fraction of predicted positives that are positive."),
        ("Recall", "TP / (TP + FN); fraction of actual positives found."),
        ("F1", "Harmonic mean of precision and recall."),
        ("Accuracy", "(TP + TN) / all test rows; compare with 88.55% majority baseline."),
    ], widths=[1.3, 4.9], font_size=8.5)
    add_body(doc, "Project outputs: output/metrics.json (final metrics), output/spark_train.log (Spark run), report/figures/ (charts), queries/analytics.js and scripts/mongo_analytics.py (MongoDB examples). The supplied DOCX includes the analytical figures; only runtime screenshots remain to be added.")

    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    architecture_path = FIG_DIR / "architecture.png"
    make_architecture_diagram(architecture_path)
    build()
