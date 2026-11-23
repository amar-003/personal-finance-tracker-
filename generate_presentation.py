"""Build a 10-slide, code-grounded PocketWise college presentation."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


OUTPUT = Path(__file__).resolve().with_name("Project_Presentation.pptx")
W, H = 13.333, 7.5
CREAM = "FAF9F6"
INK = "1E1E1E"
GREEN = "1F5E3B"
MINT = "EAF0E9"
SAGE = "78927F"
PALE = "F1F3EF"
LINE = "D9DED8"
WHITE = "FFFFFF"
MUTED = "687168"
FONT = "Calibri"


def color(hex_value: str) -> RGBColor:
    return RGBColor.from_string(hex_value)


def add_box(slide, x, y, w, h, fill, line=None, radius=True):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color(fill)
    shape.line.color.rgb = color(line or fill)
    if radius:
        shape.adjustments[0] = 0.12
    return shape


def add_text(slide, text, x, y, w, h, *, size=18, bold=False, fill=INK,
             font=FONT, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.MIDDLE,
             margin=0.02, italic=False):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    paragraph.space_before = Pt(0)
    paragraph.space_after = Pt(0)
    paragraph.line_spacing = 1.05
    run = paragraph.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color(fill)
    return shape


def add_base(prs, number, section):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color(CREAM)
    add_text(slide, "POCKETWISE  /  PROJECT PRESENTATION", 0.62, 0.28, 6.0, 0.25,
             size=9, bold=True, fill=GREEN)
    add_text(slide, section.upper(), 9.5, 0.28, 3.2, 0.25, size=9,
             bold=True, fill=MUTED, align=PP_ALIGN.RIGHT)
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.62), Inches(7.08), Inches(12.1), Inches(0.012))
    rule.fill.solid()
    rule.fill.fore_color.rgb = color(LINE)
    rule.line.fill.background()
    add_text(slide, "SMART PERSONAL FINANCE PREDICTOR & ANALYZER", 0.62, 7.13,
             8.8, 0.2, size=8, fill=MUTED)
    add_text(slide, f"{number:02d}  /  10", 11.25, 7.12, 1.45, 0.22,
             size=9, bold=True, fill=GREEN, align=PP_ALIGN.RIGHT)
    return slide


def add_heading(slide, title, kicker=None):
    if kicker:
        add_text(slide, kicker.upper(), 0.72, 0.83, 5.8, 0.28, size=10,
                 bold=True, fill=GREEN)
    add_text(slide, title, 0.72, 1.13, 11.9, 0.62, size=30, bold=True, fill=INK)


def add_bullets(slide, items, x=0.92, y=2.08, width=11.1, gap=0.94,
                size=20, box_fill=None):
    for index, item in enumerate(items):
        top = y + index * gap
        add_box(slide, x, top + 0.14, 0.12, 0.12, GREEN, GREEN)
        if box_fill:
            add_box(slide, x + 0.32, top, width - 0.32, 0.68, WHITE, LINE)
        add_text(slide, item, x + 0.34, top, width - 0.44, 0.55,
                 size=size, fill=INK)


def add_notes(slide, notes: str):
    slide.notes_slide.notes_text_frame.text = notes.strip()


def add_title_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color(CREAM)
    add_box(slide, 9.55, 0, 3.783, 7.5, GREEN, GREEN, radius=False)
    add_text(slide, "POCKETWISE  /  PROJECT PRESENTATION", 0.85, 0.65, 7.7, 0.3,
             size=10, bold=True, fill=GREEN)
    add_text(slide, "PocketWise", 0.85, 1.55, 7.8, 0.67, size=32,
             bold=True, fill=INK, font="Segoe UI")
    add_text(slide, "Smart Personal Finance\nPredictor & Analyzer", 0.85, 2.32,
             8.15, 1.35, size=27, bold=True, fill=GREEN, font="Segoe UI")
    add_text(slide, "A local tool for understanding spending and planning ahead",
             0.88, 3.9, 7.8, 0.55, size=17, fill=MUTED)
    add_box(slide, 0.85, 5.08, 7.95, 1.12, WHITE, LINE)
    add_text(slide, "STUDENT NAME  ____________________", 1.12, 5.28, 3.7, 0.26,
             size=12, fill=INK)
    add_text(slide, "ROLL NO.  ____________________", 5.05, 5.28, 3.35, 0.26,
             size=12, fill=INK)
    add_text(slide, "COLLEGE NAME  __________________________________________",
             1.12, 5.72, 6.95, 0.26, size=12, fill=INK)
    add_text(slide, "PROJECT OVERVIEW", 10.05, 1.03, 2.75, 0.3, size=10,
             bold=True, fill="C9D8CC")
    add_text(slide, "01", 10.02, 1.73, 1.3, 0.8, size=42, bold=True,
             fill=WHITE, font="Segoe UI")
    add_text(slide, "Import  /  Analyze  /  Plan", 10.05, 2.63, 2.9, 0.8,
             size=17, bold=True, fill=WHITE)
    add_text(slide, "FastAPI  ·  SQLite  ·  scikit-learn  ·  ARIMA",
             10.05, 6.25, 2.8, 0.55, size=11, fill="DCE7DE")
    add_notes(slide, "PocketWise is a local educational project for personal expense analysis. It accepts transaction CSV files, stores records in SQLite, and presents spending trends, category estimates, forecasts, budgets, savings goals, and a transparent health heuristic. Replace the student, roll number, and college placeholders before presenting.")
    return slide


def add_standard_bullets(prs, number, section, title, items, notes,
                         *, kicker=None, size=20, gap=0.95, y=2.1):
    slide = add_base(prs, number, section)
    add_heading(slide, title, kicker)
    add_bullets(slide, items, y=y, gap=gap, size=size)
    add_notes(slide, notes)
    return slide


def add_tech_slide(prs):
    slide = add_base(prs, 5, "Implementation")
    add_heading(slide, "Built with a small, practical stack", "Tech stack")
    x, y, widths = 0.8, 2.02, [2.28, 4.34, 5.06]
    headers = ["AREA", "TOOLS IN THE PROJECT", "ROLE"]
    rows = [
        ("Frontend", "HTML · CSS · JavaScript", "Responsive dashboard, CSV parsing, charts, forms"),
        ("Backend", "Python · FastAPI · Pydantic · Uvicorn", "HTTP API, validation, local app serving"),
        ("Data / ML", "SQLite · Pandas · NumPy · SciPy", "Storage, tabular processing, sparse features"),
        ("Data / ML", "scikit-learn · statsmodels", "Category classifier and ARIMA forecasting"),
    ]
    row_h = 0.72
    for col, (head, width) in enumerate(zip(headers, widths)):
        xx = x + sum(widths[:col])
        add_box(slide, xx, y, width - 0.04, 0.48, GREEN, GREEN, radius=False)
        add_text(slide, head, xx + 0.12, y + 0.04, width - 0.28, 0.34,
                 size=10, bold=True, fill=WHITE)
    for row_index, row in enumerate(rows):
        yy = y + 0.55 + row_index * row_h
        for col, (value, width) in enumerate(zip(row, widths)):
            xx = x + sum(widths[:col])
            fill = WHITE if row_index % 2 == 0 else PALE
            add_box(slide, xx, yy, width - 0.04, row_h - 0.08, fill, LINE, radius=False)
            add_text(slide, value, xx + 0.12, yy + 0.04, width - 0.28, row_h - 0.16,
                     size=14 if col else 15, bold=(col == 0),
                     fill=GREEN if col == 0 else INK)
    add_text(slide, "One local FastAPI app serves both the API and browser interface.",
             0.86, 6.02, 11.7, 0.42, size=15, fill=MUTED, italic=True)
    add_notes(slide, "The browser client is plain HTML, CSS, and JavaScript. FastAPI defines the API and serves index.html, styles.css, and app.js from the same origin. Pydantic models validate request payloads. SQLite holds transactions, budgets, and savings goals. Pandas and NumPy support tabular calculations; SciPy supplies sparse matrix support. The category model uses scikit-learn, while statsmodels provides ARIMA. Uvicorn runs the app. The project requirements also include pytest for the test suite.")
    return slide


def add_architecture_slide(prs):
    slide = add_base(prs, 6, "Data flow")
    add_heading(slide, "From transaction file to useful view", "System architecture & data flow")
    stages = [
        ("01", "CSV upload", "Browser reads file"),
        ("02", "Map & clean", "Headers, amounts, labels"),
        ("03", "Validate & store", "FastAPI → SQLite"),
        ("04", "Analyze", "Classifier · ARIMA · rules"),
        ("05", "Dashboard", "Charts, plans, estimates"),
    ]
    start, top, bw, bh, gap = 0.77, 2.47, 2.24, 1.55, 0.32
    for i, (num, label, detail) in enumerate(stages):
        xx = start + i * (bw + gap)
        add_box(slide, xx, top, bw, bh, WHITE, LINE)
        add_text(slide, num, xx + 0.15, top + 0.13, 0.48, 0.3,
                 size=11, bold=True, fill=GREEN)
        add_text(slide, label, xx + 0.15, top + 0.51, bw - 0.3, 0.38,
                 size=16, bold=True, fill=INK)
        add_text(slide, detail, xx + 0.15, top + 0.99, bw - 0.3, 0.42,
                 size=11, fill=MUTED)
        if i < len(stages) - 1:
            add_text(slide, "→", xx + bw + 0.02, top + 0.58, gap - 0.02, 0.38,
                     size=19, bold=True, fill=GREEN, align=PP_ALIGN.CENTER)
    add_box(slide, 1.1, 4.62, 11.13, 0.9, MINT, MINT)
    add_text(slide, "Local records stay in SQLite; predictions run from the stored history.",
             1.36, 4.81, 10.6, 0.48, size=16, bold=True, fill=GREEN,
             align=PP_ALIGN.CENTER)
    add_notes(slide, "The browser parses CSV rows, normalizes common date, description, amount, and category headers, and applies simple description keyword labels when categories are blank. It posts transaction records to FastAPI. Pydantic checks request shape, then the finance service preprocesses dates, descriptions, amounts, and derived features. The database layer writes transaction rows atomically to SQLite, replacing or appending based on the selected option. Category predictions train from stored labeled rows when requested; the 30-day forecast fits ARIMA from daily spend history; budgets and savings goals use their own SQLite tables. The browser calls the same-origin API and renders results.")
    return slide


def add_model_slide(prs):
    slide = add_base(prs, 7, "Models & logic")
    add_heading(slide, "Two models answer different questions", "Predictive model / logic")
    add_box(slide, 0.82, 2.03, 5.7, 3.66, WHITE, LINE)
    add_box(slide, 6.78, 2.03, 5.7, 3.66, WHITE, LINE)
    add_text(slide, "SPENDING FORECAST", 1.12, 2.31, 4.9, 0.29,
             size=10, bold=True, fill=GREEN)
    add_text(slide, "ARIMA(1, 1, 1)", 1.12, 2.78, 4.9, 0.52,
             size=23, bold=True, fill=INK)
    add_text(slide, "Daily spend = sum of absolute transaction amounts", 1.12, 3.55,
             4.9, 0.58, size=15, fill=INK)
    add_text(slide, "30 future days · negatives clipped to zero", 1.12, 4.35,
             4.9, 0.4, size=14, fill=MUTED)
    add_text(slide, "CATEGORY PREDICTION", 7.08, 2.31, 4.9, 0.29,
             size=10, bold=True, fill=GREEN)
    add_text(slide, "TF-IDF + logistic regression", 7.08, 2.78, 4.9, 0.52,
             size=21, bold=True, fill=INK)
    add_text(slide, "Description n-grams + scaled transaction amount", 7.08,
             3.55, 4.9, 0.58, size=15, fill=INK)
    add_text(slide, "Balanced classes · confidence from probabilities", 7.08,
             4.35, 4.9, 0.4, size=14, fill=MUTED)
    add_text(slide, "History checks: 14+ calendar days and spend variation for ARIMA.",
             0.94, 6.0, 11.55, 0.42, size=15, bold=True, fill=GREEN,
             align=PP_ALIGN.CENTER)
    add_notes(slide, "The forecast first groups absolute transaction amounts by calendar day and fills missing days with zero. It requires at least 14 calendar days and more than one distinct daily value, then fits statsmodels ARIMA with order (1,1,1), forecasts 30 steps, and clips negative forecasts to zero. This is a point estimate with no backtest or uncertainty interval in the current code. Category prediction is separate: it trains a TF-IDF vectorizer on one- and two-word n-grams (up to 5,000 features), standardizes amount as one additional feature, and fits scikit-learn LogisticRegression with class_weight='balanced'. The current implementation needs two labeled categories and at least two transactions per category. It reports the highest predicted class and its model probability. Neither output should be presented as guaranteed or as financial advice.")
    return slide


def add_demo_slide(prs):
    slide = add_base(prs, 8, "Demo")
    add_heading(slide, "Live demo / UI walkthrough", "Screenshots")
    labels = ["DASHBOARD", "CSV IMPORT", "FORECAST GRAPH"]
    captions = ["Daily spend and category view", "Header mapping and import controls", "30-day ARIMA estimate"]
    x0, y, w, h, gap = 0.79, 2.02, 3.83, 3.55, 0.3
    for i, (label, caption) in enumerate(zip(labels, captions)):
        xx = x0 + i * (w + gap)
        box = add_box(slide, xx, y, w, h, WHITE, SAGE)
        box.line.width = Pt(1.4)
        add_box(slide, xx + 0.16, y + 0.16, w - 0.32, h - 0.68, PALE, LINE)
        add_text(slide, "PLACE SCREENSHOT HERE", xx + 0.33, y + 1.26,
                 w - 0.66, 0.38, size=11, bold=True, fill=SAGE,
                 align=PP_ALIGN.CENTER)
        add_text(slide, label, xx + 0.18, y + h - 0.42, w - 0.36, 0.19,
                 size=9, bold=True, fill=GREEN, align=PP_ALIGN.CENTER)
        add_text(slide, caption, xx, y + h + 0.16, w, 0.36, size=12,
                 fill=MUTED, align=PP_ALIGN.CENTER)
    add_notes(slide, "Replace each outlined placeholder with a screenshot from the running application. Suggested captures: the overview with real sample transactions; the import section showing the selected CSV and replace/append option; and the forecast tab after generating the 30-day result. Use synthetic or approved sample data only. The current sample CSV is in ml/data/sample_transactions.csv. The forecasting service requires at least 14 calendar days and variation, so extend the sample dates before capturing a successful forecast if needed.")
    return slide


def add_closing_slide(prs):
    slide = add_base(prs, 10, "Next steps")
    add_heading(slide, "A useful first step; room to grow", "Future scope & conclusion")
    add_bullets(slide, [
        "Future: bank APIs and opt-in spending alerts",
        "Backtest forecasts; show uncertainty ranges",
        "Export filtered reports for personal review",
        "PocketWise turns records into clearer plans.",
    ], y=2.08, gap=0.82, size=18)
    add_box(slide, 0.92, 5.63, 11.25, 0.7, MINT, MINT)
    add_text(slide, "Thank you  ·  Questions?", 1.2, 5.77, 10.7, 0.38,
             size=18, bold=True, fill=GREEN, align=PP_ALIGN.CENTER)
    add_notes(slide, "The roadmap identifies forecast backtesting, uncertainty ranges, comparisons with actual spend, optional warning thresholds, and local report export as next priorities. Bank API integration and automated notices are practical extensions, but they are not implemented. The project currently offers a local CSV-based workflow with budgets, savings goals, transaction history, and educational estimates. End by inviting questions and replacing the presentation placeholders on slide one.")
    return slide


def build_deck() -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    prs.core_properties.title = "PocketWise: Smart Personal Finance Predictor & Analyzer"
    prs.core_properties.subject = "College project presentation"
    prs.core_properties.author = "PocketWise project team"
    add_title_slide(prs)
    add_standard_bullets(prs, 2, "Context", "Manual tracking leaves gaps",
        ["Transactions sit across statements and receipts",
         "Manual totals hide category-level patterns",
         "Irregular purchases make monthly estimates harder",
         "Repeated reviews take time and miss trends"],
        "The project addresses a common workflow problem: transaction details arrive in different records, manual grouping takes effort, and a static total says little about category patterns or daily changes. This slide describes the motivation, not a measured user study or a claim that manual tracking always fails. PocketWise focuses on importing records and making them easier to review.")
    add_standard_bullets(prs, 3, "Approach", "One local workflow for spending decisions",
        ["Import and normalize transaction CSV files",
         "Review daily and category spending patterns",
         "Estimate categories and the next 30 days",
         "Track budgets, savings goals, and health indicators"],
        "The browser interface accepts CSV transactions and maps common header variants. The dashboard provides date and description filters, spending charts, and transaction rows. A category classifier estimates labels from stored labeled examples. A separate ARIMA time series produces a 30-day daily spending forecast. The planning area stores monthly budgets and savings goals. The health estimate applies explicit rules to recent spending and user-supplied income, debt, and savings. All services operate locally through the FastAPI app and SQLite database.")
    add_standard_bullets(prs, 4, "Application", "Features grounded in the current build",
        ["CSV header mapping with description-based category defaults",
         "Daily trends, category breakdown, and transaction search",
         "Monthly budgets and savings-goal progress tracking",
         "30-day ARIMA forecast and category prediction"],
        "The CSV parser handles quoted cells and common variations in transaction date, description, amount, and category headers. If the category is absent or blank, browser-side keyword rules assign a basic category such as Housing, Groceries, or Other. The dashboard filters the stored history and draws daily and category charts. Budgets can cover all spending or one category; progress compares imported transactions with the configured limit. Savings goals store target, current amount, and date. Forecast and classifier details appear on the next slide. The health score is another current feature, shown in the solution overview and application UI.", size=17, gap=0.95)
    add_tech_slide(prs)
    add_architecture_slide(prs)
    add_model_slide(prs)
    add_demo_slide(prs)
    add_standard_bullets(prs, 9, "Engineering notes", "Practical challenges the code handles",
        ["Bank exports use inconsistent column names",
         "Sparse or flat histories cannot support ARIMA",
         "Classifier training needs enough labeled examples",
         "Import mode must protect existing local records"],
        "The browser and Python parser map aliases such as Posted Date, Payee, Debit Amount, and Money Out into a common schema, and report missing required fields. The browser parser reads UTF-8 text; unusual encodings remain a practical limitation worth testing with real bank exports. Forecasting validates at least 14 calendar days and nonconstant daily spend before fitting ARIMA. Classification requires at least two labeled categories and two rows in each category. Imports support replace or append; the database uses a transaction so the selected operation is atomic. These are code-grounded engineering constraints and mitigations, rather than invented claims about development history. A useful learning is to state model limits alongside outputs.")
    add_closing_slide(prs)
    if len(prs.slides) != 10:
        raise RuntimeError(f"Expected 10 slides, created {len(prs.slides)}")
    prs.save(OUTPUT)
    return prs


def validate_deck(path: Path) -> None:
    deck = Presentation(path)
    if len(deck.slides) != 10:
        raise AssertionError("Presentation must contain exactly 10 slides.")
    expected_width, expected_height = Inches(W), Inches(H)
    if deck.slide_width != expected_width or deck.slide_height != expected_height:
        raise AssertionError("Presentation dimensions are not 16:9 widescreen.")
    for slide_number, slide in enumerate(deck.slides, start=1):
        notes = slide.notes_slide.notes_text_frame.text.strip()
        if len(notes) < 100:
            raise AssertionError(f"Slide {slide_number} is missing detailed speaker notes.")
        for shape in slide.shapes:
            if shape.left < 0 or shape.top < 0:
                raise AssertionError(f"Slide {slide_number} has a shape outside its canvas.")
            if shape.left + shape.width > deck.slide_width:
                raise AssertionError(f"Slide {slide_number} has a shape beyond the right edge.")
            if shape.top + shape.height > deck.slide_height:
                raise AssertionError(f"Slide {slide_number} has a shape beyond the bottom edge.")
    print(f"Created and validated {path} ({len(deck.slides)} slides, 16:9, speaker notes present).")


if __name__ == "__main__":
    build_deck()
    validate_deck(OUTPUT)
