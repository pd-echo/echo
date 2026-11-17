import json

from report_models import ClientReportData
from pdf_builders import SummaryReportBuilder
# static/avkotesh@gmail.com (1).json
# static/jyothi@echo.com.json
# static/ALLA8081 (1).json
# static/agneya2001@gmail.com (1).json
# static/avkotesh@gmail.com.json
with open("static/ALLA8081 (1).json", "r", encoding="utf-8") as f:
    raw = json.load(f)

report = ClientReportData.from_dict(raw["data"])
SummaryReportBuilder("output/summary.pdf").build(report)