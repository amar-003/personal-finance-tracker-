from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets" / "screenshots"
OUT = ROOT / "smart_finance_project_presentation.pptx"

NAVY = "102A43"
NAVY_2 = "173F5F"
TEAL = "2D7D78"
GREEN = "62A982"
LIGHT = "F4F7F5"
WHITE = "FFFFFF"
TEXT = "203040"
MUTED = "66766F"
LINE = "DDE6E1"
PALE_TEAL = "EAF4F1"
PALE_GREEN = "EDF6EF"
AMBER = "D89B45"


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)


def rgb(hex_color):
    return RGBColor.from_string(hex_color)


def add_text(slide, text, x, y, w, h, size=18, color=TEXT,
             bold=False, font="Aptos", align=PP_ALIGN.LEFT,
             valign=MSO_ANCHOR.TOP, margin=0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name = font
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = rgb(color)
    return box


def add_title(slide, title, section=None):
    add_text(slide, title, 0.65, 0.42, 11.8, 0.55, 26, NAVY, True)
    if section:
        add_text(slide, section.upper(), 11.7, 0.48, 1.0, 0.25, 8, TEAL, True, align=PP_ALIGN.RIGHT)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(1.05), Inches(12.03), Inches(0.025))
    line.fill.solid()
    line.fill.fore_color.rgb = rgb(LINE)
    line.line.fill.background()


def add_footer(slide, number):
    add_text(slide, "SMART PERSONAL FINANCE PREDICTOR & ANALYZER", 0.65, 7.12, 5.8, 0.18, 8, MUTED, True)
    add_text(slide, str(number).zfill(2), 12.05, 7.08, 0.55, 0.22, 9, TEAL, True, align=PP_ALIGN.RIGHT)


def card(slide, x, y, w, h, fill=WHITE, line=LINE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    shape.line.color.rgb = rgb(line)
    shape.line.width = Pt(1)
    return shape


def pill(slide, text, x, y, w, fill=PALE_TEAL, color=TEAL):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.36))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    shape.line.fill.background()
    add_text(slide, text, x + 0.08, y + 0.06, w - 0.16, 0.20, 9, color, True, align=PP_ALIGN.CENTER)


def arrow(slide, x1, y1, x2, y2, color=TEAL):
    ln = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = rgb(color)
    ln.line.width = Pt(2)
    return ln


def add_image_cover(slide, path, x, y, w, h):
    slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w), height=Inches(h))


def new_slide(bg=LIGHT):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(bg)
    return slide


# 1 - Title
slide = new_slide(NAVY)
add_text(slide, "POCKETWISE", 0.75, 0.55, 2.5, 0.35, 10, "A9D9CE", True)
add_text(slide, "Smart Personal\nFinance Predictor\n& Analyzer", 0.75, 1.45, 7.8, 2.25, 34, WHITE, True)
add_text(slide, "A local, explainable personal-finance dashboard", 0.78, 4.05, 6.5, 0.38, 15, "C8D7D2")
card(slide, 9.55, 1.25, 2.95, 4.65, NAVY_2, "3A607B")
add_text(slide, "STUDENT", 10.05, 1.75, 1.9, 0.25, 9, "A9D9CE", True)
add_text(slide, "[Student Name]", 10.05, 2.10, 1.95, 0.55, 15, WHITE, True)
add_text(slide, "DEPARTMENT", 10.05, 2.95, 1.9, 0.25, 9, "A9D9CE", True)
add_text(slide, "B.Tech CSE (AI)", 10.05, 3.30, 1.95, 0.55, 14, WHITE, True)
add_text(slide, "COLLEGE / GUIDE", 10.05, 4.15, 1.9, 0.25, 9, "A9D9CE", True)
add_text(slide, "Teerthanker Mahaveer\nUniversity, Moradabad\n[Faculty Guide]", 10.05, 4.48, 1.95, 0.92, 11, WHITE, True)
add_text(slide, "2026  |  Project Presentation", 0.78, 6.70, 4.5, 0.28, 10, "A9D9CE", True)

# 2 - Problem
slide = new_slide()
add_title(slide, "Personal finance still feels fragmented", "01 / Problem")
card(slide, 0.65, 1.35, 7.25, 5.25)
points = [
    ("01", "Manual tracking", "Transactions are scattered across statements and notes."),
    ("02", "Hidden patterns", "It is difficult to compare categories and recurring spend."),
    ("03", "Weak planning", "Budgets and savings goals are often disconnected."),
    ("04", "Uncertain forecasting", "Past spending is not converted into a clear next-step estimate."),
]
for i, (num, head, body) in enumerate(points):
    y = 1.65 + i * 1.18
    pill(slide, num, 1.0, y, 0.52)
    add_text(slide, head, 1.70, y - 0.02, 2.7, 0.30, 16, NAVY, True)
    add_text(slide, body, 1.70, y + 0.36, 5.75, 0.48, 11, MUTED)
card(slide, 8.25, 1.35, 4.43, 5.25, PALE_TEAL, "C9DFD7")
add_text(slide, "THE GAP", 8.65, 1.75, 2.2, 0.25, 9, TEAL, True)
add_text(slide, "Data exists.\nUnderstanding does not.", 8.65, 2.18, 3.35, 1.15, 25, NAVY, True)
for i, (label, value) in enumerate([("Import", "CSV"), ("Analyze", "Local"), ("Plan", "Simple")]):
    x = 8.65 + i * 1.15
    card(slide, x, 4.05, 1.02, 1.18, WHITE)
    add_text(slide, value, x + 0.05, 4.32, 0.92, 0.24, 12, TEAL, True, align=PP_ALIGN.CENTER)
    add_text(slide, label, x + 0.05, 4.68, 0.92, 0.25, 8, MUTED, True, align=PP_ALIGN.CENTER)
add_footer(slide, 2)

# 3 - Solution
slide = new_slide()
add_title(slide, "One local flow: import, understand, plan", "02 / Solution")
steps = [
    ("1", "IMPORT", "CSV transaction history"),
    ("2", "PROCESS", "Normalize & classify"),
    ("3", "ANALYZE", "Charts, forecast, heuristic"),
    ("4", "ACT", "Budgets & savings goals"),
]
for i, (num, head, body) in enumerate(steps):
    x = 0.75 + i * 3.05
    card(slide, x, 1.75, 2.55, 2.15, WHITE)
    pill(slide, num, x + 0.18, 1.98, 0.46)
    add_text(slide, head, x + 0.18, 2.55, 2.18, 0.30, 14, NAVY, True)
    add_text(slide, body, x + 0.18, 2.95, 2.18, 0.55, 11, MUTED)
    if i < 3:
        arrow(slide, x + 2.55, 2.82, x + 3.02, 2.82)
card(slide, 0.75, 4.45, 11.82, 1.55, PALE_GREEN)
add_text(slide, "ACTUAL BENEFITS", 1.05, 4.80, 2.0, 0.25, 9, TEAL, True)
benefits = ["Flexible CSV import", "Transparent local processing", "Historical dashboards", "Interactive planning"]
for i, text in enumerate(benefits):
    add_text(slide, "●  " + text, 1.05 + i * 2.86, 5.25, 2.62, 0.30, 11, TEXT, True)
add_footer(slide, 3)

# 4 - Objectives/features
slide = new_slide()
add_title(slide, "Implemented objectives and capabilities", "03 / Features")
features = [
    ("CSV", "Column mapping", "Date, description, amount and optional category"),
    ("CHART", "Spending views", "Daily totals, category breakdown, filters"),
    ("PREDICT", "Category model", "Description text plus transaction amount"),
    ("FORECAST", "ARIMA forecast", "30-day daily expenditure estimate"),
    ("PLAN", "Budgets", "Overall and category budgets by month"),
    ("GOAL", "Savings", "Targets, progress and monthly contribution"),
]
for i, (icon, head, body) in enumerate(features):
    col = i % 3
    row = i // 3
    x = 0.65 + col * 4.12
    y = 1.48 + row * 2.38
    card(slide, x, y, 3.72, 1.92)
    pill(slide, icon, x + 0.22, y + 0.22, 0.92)
    add_text(slide, head, x + 0.22, y + 0.76, 3.20, 0.34, 16, NAVY, True)
    add_text(slide, body, x + 0.22, y + 1.18, 3.20, 0.50, 10, MUTED)
add_footer(slide, 4)

# 5 - Architecture
slide = new_slide()
add_title(slide, "Local three-tier application architecture", "04 / Architecture")
boxes = [
    (0.65, "BROWSER UI", "HTML · CSS · JavaScript"),
    (3.55, "FASTAPI", "REST endpoints & validation"),
    (6.45, "FINANCE / ML", "ARIMA · Logistic regression"),
    (9.35, "SQLITE", "Transactions · budgets · goals"),
]
for i, (x, head, body) in enumerate(boxes):
    card(slide, x, 1.75, 2.55, 1.55, WHITE)
    add_text(slide, head, x + 0.18, 2.05, 2.18, 0.30, 13, NAVY, True)
    add_text(slide, body, x + 0.18, 2.48, 2.18, 0.42, 9, MUTED)
    if i < 3:
        arrow(slide, x + 2.55, 2.52, x + 2.88, 2.52)
card(slide, 0.65, 4.05, 11.25, 1.65, PALE_TEAL)
add_text(slide, "REQUEST FLOW", 0.95, 4.38, 1.50, 0.25, 9, TEAL, True)
flow = ["Browser fetch", "FastAPI route", "Pandas / SQLite", "JSON response", "DOM update"]
for i, text in enumerate(flow):
    x = 2.25 + i * 1.72
    card(slide, x, 4.72, 1.42, 0.58, WHITE)
    add_text(slide, text, x + 0.08, 4.91, 1.26, 0.20, 8, TEXT, True, align=PP_ALIGN.CENTER)
    if i < 4:
        arrow(slide, x + 1.42, 5.01, x + 1.68, 5.01)
add_text(slide, "No external ML service or cloud database", 8.85, 6.15, 3.05, 0.28, 10, MUTED, True, align=PP_ALIGN.RIGHT)
add_footer(slide, 5)

# 6 - Stack
slide = new_slide()
add_title(slide, "Technology stack: compact and local", "05 / Technology")
groups = [
    ("FRONTEND", "HTML, CSS, JavaScript", "Responsive dashboard and API calls"),
    ("BACKEND", "Python, FastAPI, Uvicorn", "REST endpoints and request validation"),
    ("DATA", "SQLite, Pandas", "Local persistence and tabular analysis"),
    ("ML / ANALYTICS", "scikit-learn, SciPy, Statsmodels", "Classifier, TF-IDF and ARIMA"),
    ("TESTING", "pytest / unittest", "21 focused tests in the current suite"),
]
for i, (head, tech, purpose) in enumerate(groups):
    y = 1.45 + i * 1.05
    card(slide, 0.65, y, 12.03, 0.82)
    pill(slide, head, 0.85, y + 0.23, 1.65)
    add_text(slide, tech, 2.75, y + 0.16, 4.15, 0.27, 14, NAVY, True)
    add_text(slide, purpose, 7.05, y + 0.16, 5.25, 0.35, 10, MUTED)
add_footer(slide, 6)

# 7 - Workflow
slide = new_slide()
add_title(slide, "End-to-end user workflow", "06 / Workflow")
workflow = [
    ("1", "Choose CSV"),
    ("2", "Map columns"),
    ("3", "Validate rows"),
    ("4", "Store SQLite"),
    ("5", "Refresh dashboard"),
    ("6", "Select analysis"),
]
for i, (num, text) in enumerate(workflow):
    x = 0.55 + i * 2.12
    card(slide, x, 1.65, 1.72, 1.30, WHITE)
    pill(slide, num, x + 0.55, 1.85, 0.58)
    add_text(slide, text, x + 0.12, 2.38, 1.48, 0.28, 10, NAVY, True, align=PP_ALIGN.CENTER)
    if i < 5:
        arrow(slide, x + 1.72, 2.30, x + 2.08, 2.30)
card(slide, 0.65, 3.55, 12.03, 2.45, PALE_TEAL)
add_text(slide, "AT EACH ANALYSIS STEP", 0.95, 3.86, 2.25, 0.25, 9, TEAL, True)
items = [
    ("Dashboard", "Filter dates/search; aggregate spend"),
    ("Prediction", "Train from labeled local history"),
    ("Forecast", "Aggregate to daily series; fit ARIMA"),
    ("Planning", "Create/update budgets and goals"),
]
for i, (head, body) in enumerate(items):
    x = 0.95 + i * 2.88
    card(slide, x, 4.35, 2.55, 1.18, WHITE)
    add_text(slide, head, x + 0.15, 4.58, 2.25, 0.24, 12, NAVY, True)
    add_text(slide, body, x + 0.15, 4.94, 2.25, 0.38, 9, MUTED)
add_footer(slide, 7)

# 8 - Core modules
slide = new_slide()
add_title(slide, "Core modules implemented in the dashboard", "07 / Modules")
img = ASSETS / "dashboard-overview-section.png"
if img.exists():
    add_image_cover(slide, img, 0.65, 1.45, 7.15, 4.95)
else:
    card(slide, 0.65, 1.45, 7.15, 4.95)
    add_text(slide, "Screenshot placeholder\nCapture dashboard overview", 1.35, 3.30, 5.8, 1.0, 18, MUTED, True, align=PP_ALIGN.CENTER)
card(slide, 8.12, 1.45, 4.56, 4.95)
modules = [
    ("IMPORT", "CSV parsing and alias mapping"),
    ("OVERVIEW", "Metrics, charts and transactions"),
    ("PREDICT", "Merchant/category classifier"),
    ("FORECAST", "Next-30-day ARIMA estimate"),
    ("HEALTH", "Transparent risk heuristic"),
    ("PLAN", "Budgets and savings goals"),
]
for i, (head, body) in enumerate(modules):
    y = 1.73 + i * 0.74
    pill(slide, head, 8.38, y, 1.06)
    add_text(slide, body, 9.58, y + 0.06, 2.72, 0.28, 10, TEXT, True)
add_footer(slide, 8)

# 9 - ML / analytics
slide = new_slide()
add_title(slide, "Real analytics: models and limits", "08 / Analytics")
card(slide, 0.65, 1.40, 3.78, 4.95)
pill(slide, "CATEGORY CLASSIFIER", 0.95, 1.72, 1.78)
add_text(slide, "TF-IDF text features\n+ scaled amount\n+ Logistic Regression", 0.95, 2.28, 2.95, 1.15, 16, NAVY, True)
add_text(slide, "Trains on labeled rows already stored in SQLite.", 0.95, 3.72, 2.90, 0.52, 10, MUTED)
add_text(slide, "Requires:\n• 2 categories\n• 2 rows per category", 0.95, 4.55, 2.95, 0.72, 11, TEXT, True)
card(slide, 4.75, 1.40, 3.78, 4.95)
pill(slide, "30-DAY FORECAST", 5.05, 1.72, 1.55)
add_text(slide, "ARIMA(1,1,1)", 5.05, 2.28, 2.95, 0.42, 22, NAVY, True)
add_text(slide, "Daily spending series\nfrom absolute amounts\nwith 14-day minimum", 5.05, 3.00, 2.95, 1.05, 14, TEXT, True)
add_text(slide, "No reported accuracy metric or backtest is implemented.", 5.05, 4.55, 2.95, 0.72, 10, MUTED)
card(slide, 8.85, 1.40, 3.83, 4.95, PALE_TEAL)
pill(slide, "HEALTH HEURISTIC", 9.15, 1.72, 1.58)
add_text(slide, "Rule-based score", 9.15, 2.28, 2.95, 0.40, 18, NAVY, True)
add_text(slide, "Debt-to-income\nSavings rate\nEmergency-fund months\nDiscretionary spending variation", 9.15, 3.00, 2.95, 1.35, 12, TEXT)
add_text(slide, "Not a trained risk model or financial advice.", 9.15, 4.72, 2.95, 0.60, 10, MUTED, True)
add_footer(slide, 9)

# 10 - Demonstration
slide = new_slide()
add_title(slide, "Application demonstration", "09 / Demo")
images = [
    ("dashboard-overview-section.png", "01  OVERVIEW"),
    ("forecast-section.png", "02  FORECAST"),
]
for i, (fname, label) in enumerate(images):
    x = 0.65 + i * 6.05
    card(slide, x, 1.45, 5.65, 4.95)
    add_text(slide, label, x + 0.22, 1.68, 3.0, 0.24, 9, TEAL, True)
    path = ASSETS / fname
    if path.exists():
        add_image_cover(slide, path, x + 0.22, 2.08, 5.21, 3.95)
add_footer(slide, 10)

# 11 - Results / limitations
slide = new_slide()
add_title(slide, "Delivered work, limitations and next steps", "10 / Evaluation")
card(slide, 0.65, 1.40, 3.78, 4.95)
pill(slide, "IMPLEMENTED", 0.95, 1.72, 1.30)
implemented = [
    "Local CSV import",
    "SQLite persistence",
    "Analytics dashboard",
    "Classifier and ARIMA",
    "Rule-based health estimate",
    "Budgets and savings goals",
]
for i, text in enumerate(implemented):
    add_text(slide, "●  " + text, 0.95, 2.38 + i * 0.50, 2.95, 0.30, 11, TEXT, True)
card(slide, 4.75, 1.40, 3.78, 4.95)
pill(slide, "LIMITATIONS", 5.05, 1.72, 1.20, "F1E8DA", "9A6A32")
limitations = [
    "Local use only; no authentication",
    "No model evaluation/backtest",
    "ARIMA needs sufficient history",
    "Health score is heuristic",
    "No account or bank integration",
]
for i, text in enumerate(limitations):
    add_text(slide, "—  " + text, 5.05, 2.38 + i * 0.58, 3.05, 0.38, 10, TEXT)
card(slide, 8.85, 1.40, 3.83, 4.95, PALE_TEAL)
pill(slide, "FUTURE SCOPE", 9.15, 1.72, 1.38)
future = [
    "Backtests, MAE/RMSE and uncertainty",
    "Budget alerts and forecast comparison",
    "Authentication and protected storage",
    "Export, accessibility and mobile polish",
]
for i, text in enumerate(future):
    add_text(slide, "→  " + text, 9.15, 2.38 + i * 0.68, 3.05, 0.48, 10, TEXT, True)
add_text(slide, "VALIDATION  •  21 tests passed  •  2 ARIMA estimation warnings", 0.95, 6.57, 11.73, 0.28, 10, TEAL, True, align=PP_ALIGN.CENTER)
add_footer(slide, 11)

# 12 - Conclusion
slide = new_slide(NAVY)
add_text(slide, "THANK YOU", 0.75, 0.65, 2.5, 0.35, 10, "A9D9CE", True)
add_text(slide, "A practical step from\nspending data to better decisions", 0.75, 1.45, 8.4, 1.45, 32, WHITE, True)
takeaways = [
    ("01", "One local system", "Import, analyze, plan"),
    ("02", "Transparent logic", "Real ML plus an explainable heuristic"),
    ("03", "Clear boundaries", "Implemented, limited and future scope"),
]
for i, (num, head, body) in enumerate(takeaways):
    x = 0.75 + i * 3.85
    card(slide, x, 3.55, 3.45, 1.55, NAVY_2, "3A607B")
    add_text(slide, num, x + 0.20, 3.82, 0.48, 0.24, 10, "A9D9CE", True)
    add_text(slide, head, x + 0.20, 4.18, 2.95, 0.28, 14, WHITE, True)
    add_text(slide, body, x + 0.20, 4.62, 2.95, 0.28, 9, "C8D7D2")
add_text(slide, "QUESTIONS & ANSWERS", 0.75, 6.35, 4.5, 0.45, 18, "A9D9CE", True)
add_text(slide, "12", 12.05, 7.08, 0.55, 0.22, 9, "A9D9CE", True, align=PP_ALIGN.RIGHT)


prs.save(OUT)
print(f"Created {OUT}")
