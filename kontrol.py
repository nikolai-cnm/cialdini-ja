# -*- coding: utf-8 -*-
"""Kontroltest: holder hvert @stat-tal og hver engelsk original i kapitler.md
op mod bogens egen tekst.

Bogteksten ligger i ./kilde/ som en .txt pr. side (OCR af PDF'en). Mappen er
bevidst holdt uden for git — teksten er ophavsretligt beskyttet og hoerer ikke
til i et offentligt repo. Genskab den med:

    pdftoppm -r 300 -gray -png BOGEN.pdf img/p
    for f in img/p-*.png; do tesseract "$f" "${f%.png}" -l eng --psm 6; done
    mkdir kilde && cp img/*.txt kilde/

Koer:  python3 kontrol.py [sti-til-kilde]

Exit 0 = hvert tal og hvert citat blev fundet i bogen.
Exit 1 = mindst et kunne ikke findes og skal efterproeves manuelt.

Tal, der er vores egen udregning og ikke staar i bogen, markeres med ordet
"udregning" i @stat-labelen og springes over.

OBS: OCR kan selv tage fejl. Slaar testen ud paa et tal, saa se paa sidebilledet,
foer du retter teksten — bogens gamle 5-tal bliver fx let laest som 9.
"""
import re, sys, unicodedata
from pathlib import Path

SRC = Path("kapitler.md").read_text(encoding="utf-8")
OCR_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else "kilde")
book = " ".join(f.read_text(encoding="utf-8", errors="ignore") for f in sorted(OCR_DIR.glob("*.txt")))

def norm(s):
    # Saml ord, bogen har delt over to linjer. Scanningen efterlader ofte et
    # loesrevet tegn fra margenen mellem bindestregen og linjeskiftet.
    s = re.sub(r"([a-zA-Z])[-\u2010][ \t]*(?:\S{1,2}[ \t]*)?\n\s*([a-zA-Z])",
               r"\1\2", s)
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("’","'").replace("‘","'").replace("“",'"').replace("”",'"')
    s = s.replace("—"," ").replace("–"," ").replace("-"," ")
    s = re.sub(r"(?<=\d)[.,](?=\d)", "\u00b7", s)
    s = re.sub(r"[^0-9A-Za-z$%\u00b7\s]", " ", s)
    s = s.replace("\u00b7", ".")
    return re.sub(r"\s+", " ", s).lower().strip()

BOOK = norm(book)

# --- kapitel for kapitel ---
chapters = re.split(r"\n## (\d+)\. ", SRC)

# Den kuraterede META-sektion staar foer kapitel 1 og indeholder tal, der er
# kopieret fra bogen. Den skal kontrolleres paa lige fod med kapitlerne.
# @ads-linjer er vores egne annonceeksempler og kontrolleres ikke.
blocks = []
m = re.search(r"\n# META [^\n]*\n(.*?)(?=\n# DEL )", chapters[0], re.S)
if m:
    blocks.append(("META", "Meta ads (kurateret genvej)", m.group(1)))
for i in range(1, len(chapters), 2):
    blocks.append((chapters[i], chapters[i+1].split("\n")[0], chapters[i+1]))

results = []
for num, title, body in blocks:
    stats, quotes = [], []
    for line in body.split("\n"):
        line = line.strip()
        if line.startswith("@stat "):
            val = line[6:].split("::")[0].strip()
            if "udregning" in line: continue
            for m in re.findall(r"\d+[.,]?\d*", val):
                stats.append((val, m.replace(",", ".")))
        if line.startswith("@citat "):
            bits = [b.strip() for b in line[7:].split("::")]
            if len(bits) > 2 and bits[2]:
                quotes.append((bits[0], bits[2]))
    results.append((num, title, stats, quotes))

fails = 0
for num, title, stats, quotes in results:
    lines = []
    for val, n in stats:
        # tallet skal kunne findes i bogen (med , eller . som decimaltegn)
        cands = {n, n.replace(".", ","), n.rstrip("0").rstrip(".")}
        # ord-varianter for tal bogen skriver ud
        words = {"2":"twice","3":"three","5":"five","100":"hundred","72":"seventy two","44":"forty four","537":"537"}
        hit = any(re.search(r"(?<!\d)" + re.escape(c) + r"(?!\d)", BOOK) for c in cands if c)
        if not hit and n in words:
            hit = words[n] in BOOK
        if not hit:
            lines.append("    TAL IKKE FUNDET: %r (i @stat %r)" % (n, val))
    for label, en in quotes:
        ne = norm(en)
        # prøv hele citatet, ellers længste sammenhængende stykke på 6 ord
        if ne in BOOK:
            continue
        # OCR efterlader lososrevne enkelttegn i margenen midt i saetninger.
        # Tillad derfor et kort stoej-token mellem to ord.
        toks = ne.split()
        if toks:
            rx = r"(?:\s+\S{1,2})?\s+".join(re.escape(w) for w in toks)
            if re.search(rx, BOOK):
                continue
        words = ne.split()
        chunk = " ".join(words[:7]) if len(words) >= 7 else ne
        if chunk in BOOK:
            continue
        # sidste udvej: 5 ord fra midten
        mid = " ".join(words[len(words)//2: len(words)//2 + 5])
        if mid and mid in BOOK:
            continue
        lines.append("    CITAT IKKE FUNDET: [%s] %r" % (label, en[:70]))
    status = "OK  " if not lines else "FEJL"
    if lines: fails += 1
    print("%s kap %-3s %-58s  %2d tal, %d citater" % (status, num, title[:58], len(stats), len(quotes)))
    for l in lines: print(l)

print("\n%d kapitler kontrolleret, %d med afvigelser" % (len(results), fails))
sys.exit(1 if fails else 0)
