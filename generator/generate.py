# -*- coding: utf-8 -*-
"""Nyári Tanoda 2026 – napi PDF munkalapok generátora.

Futtatás:  python3 generate.py
Kimenet:   ../pdf/anna/*.pdf  és  ../pdf/lotti/*.pdf
Időszak:   2026. július 6. – augusztus 31. (57 nap)
"""
import math
import random
from datetime import date, timedelta
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether)
from reportlab.graphics.shapes import Drawing, Circle, Line, String, PolyLine, Rect
from reportlab.graphics import renderPDF

import data as D

# ----------------------------------------------------------------- betűtípus
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVu", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", f"{FONT_DIR}/DejaVuSans-Oblique.ttf"))

START = date(2026, 7, 6)
END = date(2026, 8, 31)

ANNA_SZIN = colors.HexColor("#1d6fb8")   # kék
LOTTI_SZIN = colors.HexColor("#c2185b")  # pink
ARANY = colors.HexColor("#f5a623")
HALVANY = colors.HexColor("#f4f6f8")

ASCII_NAP = ["hetfo", "kedd", "szerda", "csutortok", "pentek", "szombat", "vasarnap"]


def stilusok(fo_szin):
    return dict(
        cim=ParagraphStyle("cim", fontName="DejaVu-Bold", fontSize=17,
                           textColor=fo_szin, alignment=TA_CENTER, spaceAfter=2),
        alcim=ParagraphStyle("alcim", fontName="DejaVu", fontSize=10.5,
                             textColor=colors.HexColor("#555555"),
                             alignment=TA_CENTER, spaceAfter=6),
        fejezet=ParagraphStyle("fejezet", fontName="DejaVu-Bold", fontSize=11.5,
                               textColor=colors.white, backColor=fo_szin,
                               borderPadding=(3, 6, 3, 6), spaceBefore=8,
                               spaceAfter=4, leading=15),
        szoveg=ParagraphStyle("szoveg", fontName="DejaVu", fontSize=10.5,
                              leading=15, spaceAfter=3),
        felirat=ParagraphStyle("felirat", fontName="DejaVu-Oblique", fontSize=9.5,
                               textColor=colors.HexColor("#666666"), leading=13),
        teaser=ParagraphStyle("teaser", fontName="DejaVu-Bold", fontSize=11,
                              textColor=colors.HexColor("#7a4d00"),
                              backColor=colors.HexColor("#fff3d6"),
                              borderPadding=(6, 8, 6, 8), leading=15, spaceBefore=10),
        nagy=ParagraphStyle("nagy", fontName="DejaVu-Bold", fontSize=13, leading=18,
                            spaceAfter=4),
    )


# ------------------------------------------------------------------- rajzok
def ora_rajz(h, m, r=1.55 * cm, kez_nelkul=False):
    """Analóg óra rajza. kez_nelkul=True esetén üres számlap (mutatót rajzol a gyerek)."""
    d = Drawing(2 * r + 8, 2 * r + 8)
    cx = cy = r + 4
    d.add(Circle(cx, cy, r, strokeColor=colors.black, strokeWidth=1.6,
                 fillColor=colors.white))
    for i in range(1, 13):
        ang = math.radians(90 - i * 30)
        d.add(String(cx + (r - 9) * math.cos(ang) - 3.4,
                     cy + (r - 9) * math.sin(ang) - 3.4,
                     str(i), fontName="DejaVu-Bold", fontSize=8))
    for i in range(60):
        ang = math.radians(i * 6)
        r1 = r - (4 if i % 5 == 0 else 2)
        d.add(Line(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang),
                   cx + r * math.cos(ang), cy + r * math.sin(ang),
                   strokeColor=colors.grey, strokeWidth=0.6))
    if not kez_nelkul:
        ha = math.radians(90 - ((h % 12) + m / 60.0) * 30)
        ma = math.radians(90 - m * 6)
        d.add(Line(cx, cy, cx + 0.52 * r * math.cos(ha), cy + 0.52 * r * math.sin(ha),
                   strokeColor=colors.black, strokeWidth=2.6))
        d.add(Line(cx, cy, cx + 0.8 * r * math.cos(ma), cy + 0.8 * r * math.sin(ma),
                   strokeColor=ANNA_SZIN, strokeWidth=1.6))
    d.add(Circle(cx, cy, 2, fillColor=colors.black))
    return d


def pottyok(n, szimb="kor", szin=colors.HexColor("#c2185b")):
    """n darab megszámolható alakzat Lottinak (max 2 sor)."""
    per_sor = min(n, 6)
    sorok = math.ceil(n / per_sor)
    d = Drawing(per_sor * 34 + 6, sorok * 34 + 6)
    for i in range(n):
        x = 20 + (i % per_sor) * 34
        y = d.height - 20 - (i // per_sor) * 34
        if szimb == "kor":
            d.add(Circle(x, y, 10, fillColor=szin, strokeColor=colors.black,
                         strokeWidth=0.8))
        elif szimb == "haromszog":
            d.add(PolyLine([x - 11, y - 9, x, y + 11, x + 11, y - 9, x - 11, y - 9],
                           strokeColor=colors.black, strokeWidth=0.8))
        else:  # csillag
            pts = []
            for k in range(11):
                rr = 12 if k % 2 == 0 else 5
                a = math.radians(90 + k * 36)
                pts += [x + rr * math.cos(a), y + rr * math.sin(a)]
            d.add(PolyLine(pts, strokeColor=colors.black, strokeWidth=0.9))
    return d


def vonalvezeto(tipus):
    """Szaggatott gyakorlóvonal Lottinak."""
    w, h = 15.5 * cm, 1.5 * cm
    d = Drawing(w, h)
    dash = [4, 4]
    if tipus == 0 or tipus == 4:  # egyenes / pontozott egyenes
        d.add(Line(10, h / 2, w - 10, h / 2, strokeColor=colors.grey,
                   strokeWidth=1.4, strokeDashArray=dash))
    elif tipus == 1:  # hullám
        pts = []
        for i in range(0, 121):
            x = 10 + i * (w - 20) / 120.0
            pts += [x, h / 2 + 14 * math.sin(i / 120.0 * 6 * math.pi)]
        d.add(PolyLine(pts, strokeColor=colors.grey, strokeWidth=1.4,
                       strokeDashArray=dash))
    elif tipus == 2:  # cikkcakk
        pts = []
        n = 10
        for i in range(n + 1):
            x = 10 + i * (w - 20) / n
            pts += [x, h - 8 if i % 2 == 0 else 8]
        d.add(PolyLine(pts, strokeColor=colors.grey, strokeWidth=1.4,
                       strokeDashArray=dash))
    else:  # kör
        d.add(Circle(w / 2, h / 2, h / 2 - 4, strokeColor=colors.grey,
                     strokeWidth=1.4, fillColor=None, strokeDashArray=dash))
    return d


# ------------------------------------------------------------ Anna – matek
def anna_matek(het, rnd, hetvege):
    """(cím, [példák]) az adott hétre, napi véletlen számokkal."""
    db = 4 if hetvege else 8
    p = []
    if het == 0:
        cim = "Összeadás 20-ig"
        for _ in range(db):
            a = rnd.randint(3, 12); b = rnd.randint(2, 20 - a)
            p.append(f"{a} + {b} = ____")
    elif het == 1:
        cim = "Kivonás 20-ig"
        for _ in range(db):
            a = rnd.randint(8, 20); b = rnd.randint(2, a - 1)
            p.append(f"{a} − {b} = ____")
    elif het == 2:
        cim = "Számolás 100-ig (tízesátlépés nélkül)"
        for _ in range(db):
            if rnd.random() < 0.5:
                a = rnd.randint(2, 8) * 10 + rnd.randint(1, 4)
                b = rnd.randint(1, 5)
                p.append(f"{a} + {b} = ____")
            else:
                a = rnd.randint(2, 9) * 10
                b = rnd.randint(1, 9) * 10
                if b > a: a, b = b, a
                p.append(f"{a} − {b} = ____")
    elif het == 3:
        cim = "Összeadás és kivonás 100-ig (tízesátlépéssel)"
        for _ in range(db):
            if rnd.random() < 0.5:
                a = rnd.randint(15, 78); b = rnd.randint(5, 9)
                p.append(f"{a} + {b} = ____")
            else:
                a = rnd.randint(22, 95); b = rnd.randint(5, 9)
                p.append(f"{a} − {b} = ____")
    elif het == 4:
        cim = "Pótlás és nyitott mondatok"
        for _ in range(db):
            c = rnd.randint(20, 90); a = rnd.randint(5, c - 5)
            p.append(rnd.choice([f"{a} + ____ = {c}", f"____ + {c - a} = {c}",
                                 f"{c} − ____ = {a}"]))
    elif het == 5:
        cim = "Ismerkedés a szorzással: a 2-es szorzótábla"
        for _ in range(db):
            n = rnd.randint(1, 10)
            p.append(rnd.choice([f"2 · {n} = ____",
                                 f"{n} + {n} = ____  (ez ugyanaz, mint 2 · {n})"]))
    elif het == 6:
        cim = "Szorzás 5-tel és 10-zel"
        for _ in range(db):
            n = rnd.randint(1, 10)
            p.append(f"{rnd.choice([5, 10])} · {n} = ____")
    elif het == 7:
        cim = "Vegyes műveletek"
        for _ in range(db):
            v = rnd.random()
            if v < 0.4:
                a = rnd.randint(15, 80); b = rnd.randint(5, 15)
                p.append(f"{a} {rnd.choice(['+', '−'])} {b} = ____")
            elif v < 0.7:
                n = rnd.randint(1, 10)
                p.append(f"{rnd.choice([2, 5, 10])} · {n} = ____")
            else:
                a = rnd.randint(10, 40); b = rnd.randint(2, 9); c = rnd.randint(2, 9)
                p.append(f"{a} + {b} − {c} = ____")
    else:
        cim = "Nagy ismétlés – ilyen ügyes lettél a nyáron!"
        minta = [f"{rnd.randint(30, 80)} + {rnd.randint(5, 9)} = ____",
                 f"{rnd.randint(40, 95)} − {rnd.randint(5, 9)} = ____",
                 f"2 · {rnd.randint(2, 10)} = ____",
                 f"5 · {rnd.randint(2, 10)} = ____",
                 f"10 · {rnd.randint(2, 9)} = ____",
                 f"{rnd.randint(20, 60)} + ____ = {rnd.randint(70, 99)}"]
        p = minta[:db]
    return cim, p


def kis_teaser_anna(nap_idx, het_holnap, tema_holnap, rnd):
    ny = D.ANNA_NYELVTAN[min(nap_idx + 1, len(D.ANNA_NYELVTAN) - 1)][0]
    szo = rnd.choice(tema_holnap["angol"])
    matek_cim, _ = anna_matek(het_holnap, random.Random(999 + nap_idx), False)
    return (f"★ HOLNAPI KALAND ★  Nyelvtanból jön: „{ny}”. Matekból: {matek_cim.lower()}. "
            f"Angolul megtanulod, mit jelent a(z) „{szo[0]}” szó… "
            f"Vajon kitalálod előre? Holnap találkozunk!")


def kis_teaser_lotti(nap_idx, tema_holnap, rnd):
    allat = tema_holnap["lotti_allat"][(nap_idx + 1) % 7]
    szam = (nap_idx + 1) % 10 + 1
    szo = rnd.choice(tema_holnap["angol"])
    return (f"★ HOLNAPI KALAND ★  Holnap a(z) {szam}-es szám lesz a vendégünk, "
            f"találkozol egy {allat} figurával, és angolul is tanulsz egy titkos szót: "
            f"„{szo[0]}”… Vajon mit jelenthet? Aludj jól, holnap kiderül!")


# ----------------------------------------------------------- Anna – oldal
def anna_pdf(d0, nap_idx, utvonal):
    het = min(nap_idx // 7, 8)
    tema = D.TEMAK[het]
    hetnap = d0.weekday()
    hetvege = hetnap >= 5
    rnd = random.Random(20260000 + nap_idx)
    st = stilusok(ANNA_SZIN)

    doc = SimpleDocTemplate(str(utvonal), pagesize=A4,
                            leftMargin=1.4 * cm, rightMargin=1.4 * cm,
                            topMargin=1.1 * cm, bottomMargin=1.0 * cm,
                            title=f"Anna – {d0.isoformat()}")
    s = []
    s.append(Paragraph(f"ANNA NYÁRI TANODÁJA – {nap_idx + 1}. nap", st["cim"]))
    s.append(Paragraph(f"2026. {D.HONAPOK[d0.month - 1]} {d0.day}., {D.NAPOK[hetnap]} "
                       f"&nbsp;•&nbsp; A hét témája: {tema['nev']}", st["alcim"]))

    # Naptár-bemelegítő
    s.append(Paragraph("1. Naptár-bemelegítő", st["fejezet"]))
    s.append(Paragraph("Ma ______________ van. Tegnap ______________ volt. "
                       "Holnap ______________ lesz.", st["szoveg"]))
    naptar_extra = [
        "Melyik hónapban vagyunk? Hányadik hónap ez az évben? ______________",
        "Sorold fel a hét napjait fejből! Hány nap van egy héten? ____",
        "Melyik évszak van most? Sorold fel mind a négy évszakot!",
        "Hány hónapból áll egy év? ____  Melyik a te születési hónapod?",
        "Írd le a mai dátumot számokkal: ________ . ____ . ____ .",
        "Melyik hónap jön a mostani után? ______________",
        "Hány nap van még hátra ebből a hónapból? Számold ki! ____",
    ]
    s.append(Paragraph(naptar_extra[nap_idx % len(naptar_extra)], st["szoveg"]))

    # Nyelvtan
    ny_cim, ny_feladat = D.ANNA_NYELVTAN[min(nap_idx, len(D.ANNA_NYELVTAN) - 1)]
    s.append(Paragraph(f"2. Nyelvtan – {ny_cim}", st["fejezet"]))
    s.append(Paragraph(ny_feladat, st["szoveg"]))
    s.append(Paragraph("_" * 92, st["felirat"]))
    s.append(Paragraph("_" * 92, st["felirat"]))

    # Matek
    m_cim, peldak = anna_matek(het, rnd, hetvege)
    s.append(Paragraph(f"3. Matematika – {m_cim}", st["fejezet"]))
    fel = peldak[::2]; le = peldak[1::2]
    sorok = []
    for i in range(max(len(fel), len(le))):
        sorok.append([fel[i] if i < len(fel) else "",
                      le[i] if i < len(le) else ""])
    t = Table(sorok, colWidths=[8.6 * cm, 8.6 * cm])
    t.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
                           ("FONTSIZE", (0, 0), (-1, -1), 11.5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    s.append(t)
    szoveges = D.ANNA_SZOVEGES[het % len(D.ANNA_SZOVEGES)].format(
        a=rnd.randint(12, 45), b=rnd.randint(3, 11))
    s.append(Paragraph(f"Szöveges feladat: {szoveges}", st["szoveg"]))
    s.append(Paragraph("Számolás: ____________________  Válasz: ____________________",
                       st["felirat"]))

    # Óraolvasás
    ora_cim, idok = D.ORA_HETEK[het]
    valasztott = rnd.sample(idok, min(3, len(idok)))
    rajzolos = het >= 3 and nap_idx % 2 == 1
    s.append(Paragraph(f"4. Óraolvasás – {ora_cim}", st["fejezet"]))
    if rajzolos:
        s.append(Paragraph("Rajzold be a mutatókat a megadott időhöz! "
                           "(A rövid mutató az óra, a hosszú a perc.)", st["szoveg"]))
    else:
        s.append(Paragraph("Hány órát mutatnak az órák? Írd a vonalra!", st["szoveg"]))
    cellak, alairas = [], []
    for (h, m) in valasztott:
        cellak.append(ora_rajz(h, m, kez_nelkul=rajzolos))
        alairas.append(f"{h}:{m:02d}" if rajzolos else "__________")
    t = Table([cellak, alairas], colWidths=[5.7 * cm] * 3)
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                           ("FONTNAME", (0, 1), (-1, 1), "DejaVu-Bold"),
                           ("FONTSIZE", (0, 1), (-1, 1), 11),
                           ("TOPPADDING", (0, 1), (-1, 1), 4)]))
    s.append(t)

    # Angol
    szavak = [tema["angol"][(nap_idx * 2 + k) % len(tema["angol"])] for k in range(4)]
    s.append(Paragraph(f"5. Angol – {tema['angol_tema']}", st["fejezet"]))
    s.append(Paragraph("Olvasd fel hangosan háromszor, majd írd le egyszer mindegyiket!",
                       st["szoveg"]))
    t = Table([[f"{en} = {hu}" for en, hu in szavak[:2]],
               [f"{en} = {hu}" for en, hu in szavak[2:]],
               ["_______________", "_______________"]],
              colWidths=[8.6 * cm, 8.6 * cm])
    t.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
                           ("FONTSIZE", (0, 0), (-1, -1), 11),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    s.append(t)

    # Környezetismeret
    kor = D.ANNA_KORNYEZET[het][min(hetnap, len(D.ANNA_KORNYEZET[het]) - 1)]
    s.append(Paragraph("6. Környezetismeret – A hét témája nyomában", st["fejezet"]))
    s.append(Paragraph(kor, st["szoveg"]))

    # Teaser
    if d0 < END:
        het_h = min((nap_idx + 1) // 7, 8)
        s.append(Paragraph(kis_teaser_anna(nap_idx, het_h, D.TEMAK[het_h], rnd),
                           st["teaser"]))
    else:
        s.append(Paragraph("★ GRATULÁLOK! ★  Végigcsináltad a teljes nyári tanodát! "
                           "Holnap kezdődik az iskola – büszke lehetsz magadra, "
                           "másodikos leszel, és mindenre készen állsz!", st["teaser"]))
    doc.build(s)


# ----------------------------------------------------------- Lotti – oldal
def lotti_pdf(d0, nap_idx, utvonal):
    het = min(nap_idx // 7, 8)
    tema = D.TEMAK[het]
    hetnap = d0.weekday()
    hetvege = hetnap >= 5
    rnd = random.Random(50260000 + nap_idx)
    st = stilusok(LOTTI_SZIN)

    doc = SimpleDocTemplate(str(utvonal), pagesize=A4,
                            leftMargin=1.4 * cm, rightMargin=1.4 * cm,
                            topMargin=1.1 * cm, bottomMargin=1.0 * cm,
                            title=f"Lotti – {d0.isoformat()}")
    s = []
    s.append(Paragraph(f"LOTTI OVIS TANODÁJA – {nap_idx + 1}. nap", st["cim"]))
    s.append(Paragraph(f"2026. {D.HONAPOK[d0.month - 1]} {d0.day}., {D.NAPOK[hetnap]} "
                       f"&nbsp;•&nbsp; A hét témája: {tema['nev']}", st["alcim"]))
    s.append(Paragraph("(Szülővel közösen, játékosan! Egy-egy feladat 5–10 perc.)",
                       st["felirat"]))

    # A nap köszöntése
    s.append(Paragraph("1. Jó reggelt, kis okos!", st["fejezet"]))
    s.append(Paragraph(f"Mondd ki szépen: ma <b>{D.NAPOK[hetnap]}</b> van! "
                       "Milyen az idő ma? Mutasd: süt a nap, esik az eső, vagy fúj a szél?",
                       st["szoveg"]))

    # A nap száma
    szam = nap_idx % 10 + 1
    szimb = ["kor", "csillag", "haromszog"][nap_idx % 3]
    s.append(Paragraph(f"2. A nap száma: {szam}", st["fejezet"]))
    s.append(Paragraph(f"Számold meg az alakzatokat! Tényleg {szam} darab van? "
                       f"Mutasd az ujjaidon is a(z) {szam}-t!", st["szoveg"]))
    s.append(pottyok(szam, szimb, LOTTI_SZIN if szimb == "kor" else colors.black))
    s.append(Paragraph(f"Keress a lakásban {szam} egyforma tárgyat (pl. kanalat, kockát), "
                       "és számoljátok meg együtt!", st["szoveg"]))

    # Forma és szín
    forma = D.LOTTI_FORMAK[nap_idx % len(D.LOTTI_FORMAK)]
    szin = D.LOTTI_SZINEK[nap_idx % len(D.LOTTI_SZINEK)]
    s.append(Paragraph(f"3. Forma és szín: {forma} + {szin}", st["fejezet"]))
    s.append(Paragraph(f"Rajzolj egy nagy <b>{forma}</b> alakzatot, és színezd "
                       f"<b>{szin}</b>re! Keress a szobában valamit, ami {szin} színű!",
                       st["szoveg"]))
    s.append(Spacer(1, 1.6 * cm))

    # Betű-játék
    betu = D.LOTTI_BETUK[nap_idx % len(D.LOTTI_BETUK)]
    s.append(Paragraph(f"4. Betűvarázs: {betu}", st["fejezet"]))
    s.append(Paragraph(f"Ez itt egy nagy <b>{betu}</b> betű! Mondd ki a hangját! "
                       f"Mondj egy szót, ami így kezdődik! Rajzold át az ujjaddal, "
                       f"majd a levegőbe is írd le nagyban!", st["szoveg"]))
    dr = Drawing(3 * cm, 2.4 * cm)
    dr.add(String(0.6 * cm, 0.4 * cm, betu, fontName="DejaVu-Bold", fontSize=52,
                  fillColor=LOTTI_SZIN))
    s.append(dr)

    # Angol
    szavak = [tema["angol"][(nap_idx + k) % len(tema["angol"])] for k in range(2)]
    s.append(Paragraph("5. Angol szavacskák", st["fejezet"]))
    s.append(Paragraph(" &nbsp;&nbsp; ".join(f"<b>{en}</b> = {hu}" for en, hu in szavak) +
                       " — Mondd ki háromszor, jó hangosan, jó viccesen is!", st["szoveg"]))

    # A hét témája – állatos/figurás feladat
    allat = tema["lotti_allat"][hetnap % len(tema["lotti_allat"])]
    s.append(Paragraph(f"6. A nap figurája: {allat}", st["fejezet"]))
    jatek = [
        f"Utánozd, hogyan mozog vagy milyen hangot ad a(z) {allat}! ",
        f"Rajzold le a(z) {allat} figurát, ahogy csak tudod! ",
        f"Mesélj róla: mit eszik, hol lakik a(z) {allat}? ",
        f"Játsszatok: a szülő mutogatja a(z) {allat} figurát, te kitalálod! ",
    ]
    s.append(Paragraph(jatek[nap_idx % len(jatek)] +
                       "Utána keressetek róla egy képet egy könyvben!", st["szoveg"]))

    # Mondóka + finommotorika (hétvégén mondóka-ismétlés)
    mondoka = D.LOTTI_MONDOKAK[nap_idx % len(D.LOTTI_MONDOKAK)]
    s.append(Paragraph("7. Mondóka és ügyes kezek", st["fejezet"]))
    if hetvege:
        s.append(Paragraph(f"Hétvégi ráadás: ismételjétek el a hét kedvenc mondókáját! "
                           f"Mai ötlet: {mondoka}", st["szoveg"]))
    else:
        s.append(Paragraph(f"Mondjátok együtt: <b>{mondoka}</b>", st["szoveg"]))
    mot_idx = nap_idx % len(D.LOTTI_MOTOROS)
    s.append(Paragraph(D.LOTTI_MOTOROS[mot_idx], st["szoveg"]))
    s.append(vonalvezeto(mot_idx))

    # Teaser
    if d0 < END:
        s.append(Paragraph(kis_teaser_lotti(nap_idx, D.TEMAK[min((nap_idx + 1) // 7, 8)],
                                            rnd), st["teaser"]))
    else:
        s.append(Paragraph("★ HURRÁ! ★  Az egész nyarat végigjátszottad-tanultad! "
                           "Holnaptól újra ovi – meséld el a barátaidnak, mennyi "
                           "mindent tudsz már!", st["teaser"]))
    doc.build(s)


# ------------------------------------------------------------------ futtatás
def main():
    gyoker = Path(__file__).resolve().parent.parent
    d0, idx = START, 0
    while d0 <= END:
        nev = f"nap{idx + 1:02d}_{d0.isoformat()}_{ASCII_NAP[d0.weekday()]}.pdf"
        anna_pdf(d0, idx, gyoker / "pdf" / "anna" / nev)
        lotti_pdf(d0, idx, gyoker / "pdf" / "lotti" / nev)
        d0 += timedelta(days=1)
        idx += 1
    print(f"Kész: {idx} nap × 2 gyerek = {idx * 2} PDF")


if __name__ == "__main__":
    main()
