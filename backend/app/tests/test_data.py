"""
File: test_data.py
Project: tests
File Created: Tuesday, 18th November 2025 9:05:23 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Tuesday, 18th November 2025 9:14:43 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""


import os
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "test"))
os.makedirs(ROOT, exist_ok=True)

# 1) small legal act (JSON) - good for basic smoke tests
small_act = {
    "source": "data/acts/companies_act_2025.pdf",
    "title": "Companies Act 2025",
    "text": (
        "Part I — Preliminary\n\n"
        "1. Short title and commencement. This Act may be cited as the Companies Act 2025.\n\n"
        "2. Interpretation. In this Act, unless the context otherwise requires —\n"
        "   'company' means a body corporate formed and registered under this Act.\n\n"
        "Part II — Incorporation\n\n"
        "3. Incorporation process: An application for incorporation must be made in the prescribed form."
    ),
    "metadata": {"category": "act", "jurisdiction": "Ghana", "page": 1}
}
with open(os.path.join(ROOT, "small_act.json"), "w", encoding="utf-8") as f:
    json.dump(small_act, f, ensure_ascii=False, indent=2)

# 2) long judgment (plain text) — repeats a paragraph to force multiple chunks
para = (
    "The Court considered the application and held that the principles of natural justice "
    "require that a hearing be afforded to the applicant. The reasons given include the "
    "importance of procedural fairness in administrative decisions and the impact on fundamental rights. "
)
long_text = para * 200  # ~ thousands of characters to exercise chunking
with open(os.path.join(ROOT, "long_judgment.txt"), "w", encoding="utf-8") as f:
    f.write("Case: Republic v. Commissioner of Lands\n\n")
    f.write("Judgment Summary:\n\n")
    f.write(long_text)

# 3) simulated OCR output (plain text) — contains typical OCR artifacts
ocr_sim = (
    "Plaintiff v. Defendant\n\n"
    "¶ 1. The above-named parties appeared before the Court on 01/02/2010.\n"
    "¶ 2. The document contains OCR errors: th1s, examp1e, li-\n"
    "ne broken words and random ß characters.\n\n"
    "The Court finds as follows..."
)
with open(os.path.join(ROOT, "ocr_simulated.txt"), "w", encoding="utf-8") as f:
    f.write(ocr_sim)

# 4) dict-form document (for direct Ingestor.ingest calls)
dict_doc = {
    "source": "http://example.gov.gh/regulations/environment_li_2024.pdf",
    "title": "Environmental Regulations LI 2024",
    "text": (
        "Regulation 1. These Regulations shall apply to all activities that may impact the environment.\n\n"
        "Regulation 2. Failure to comply with any provision is an offence punishable by a fine."
    ),
    "metadata": {"category": "regulation", "year": 2024}
}
with open(os.path.join(ROOT, "dict_doc.json"), "w", encoding="utf-8") as f:
    json.dump(dict_doc, f, ensure_ascii=False, indent=2)
