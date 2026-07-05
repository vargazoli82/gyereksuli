# -*- coding: utf-8 -*-
"""Elküldi e-mailben az aznapi tanoda-PDF-eket (Anna + Lotti).

A GitHub Actions futtatja minden reggel. Szükséges környezeti változók:
  GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT
"""
import os
import smtplib
import sys
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

START = date(2026, 7, 6)
END = date(2026, 8, 31)
ASCII_NAP = ["hetfo", "kedd", "szerda", "csutortok", "pentek", "szombat", "vasarnap"]
NAPOK = ["hétfő", "kedd", "szerda", "csütörtök", "péntek", "szombat", "vasárnap"]

# Magyar idő (nyáron UTC+2)
ma = (datetime.now(timezone.utc) + timedelta(hours=2)).date()
ma = date(2026, 7, 6)  # TESZT - torlendo

if not (START <= ma <= END):
    print(f"Ma ({ma}) nincs tananyag – a tanoda {START} és {END} között tart.")
    sys.exit(0)

idx = (ma - START).days + 1
fajlnev = f"nap{idx:02d}_{ma.isoformat()}_{ASCII_NAP[ma.weekday()]}.pdf"
gyoker = Path(__file__).resolve().parent.parent

msg = EmailMessage()
msg["From"] = os.environ["GMAIL_USER"]
msg["To"] = os.environ["RECIPIENT"]
msg["Subject"] = f"🌞 Nyári Tanoda – {idx}. nap ({ma.isoformat()}, {NAPOK[ma.weekday()]})"

utolso = (END - ma).days
zaras = ("Ma van az utolsó nap – holnap iskola és ovi! 🎒"
         if utolso == 0 else f"Még {utolso} nap van hátra a tanodából.")
msg.set_content(
    f"Szia!\n\n"
    f"Itt a mai tananyag Annának és Lottinak ({idx}. nap, {NAPOK[ma.weekday()]}).\n"
    f"A két PDF csatolva – jó tanulást!\n\n{zaras}\n\n"
    f"A teljes tananyag: https://github.com/vargazoli82/gyereksuli\n"
)

hianyzik = []
for gyerek in ("anna", "lotti"):
    p = gyoker / "pdf" / gyerek / fajlnev
    if p.exists():
        msg.add_attachment(p.read_bytes(), maintype="application",
                           subtype="pdf", filename=f"{gyerek}_{fajlnev}")
    else:
        hianyzik.append(str(p))

if hianyzik:
    print("HIBA – nem található:", *hianyzik, sep="\n")
    sys.exit(1)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"])
    smtp.send_message(msg)

print(f"Elküldve: {fajlnev} (Anna + Lotti) → {os.environ['RECIPIENT']}")
