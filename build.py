#!/usr/bin/env python3
"""Bygger index.html ud fra kapitler.md. Én selvstændig fil uden eksterne assets.

Markdown-dialekt:
  # DEL n — titel          ->  del-overskrift (grupperer kapitler i navigationen)
  ## n. Titel              ->  kapitel
  @princip X               ->  princip-mærkat på kapitlet (kan filtreres på)
  @side X                  ->  kildehenvisning på kapitlet
  > tekst                  ->  kernen i kapitlet (står altid åbent)
  ### Blok n · Titel       ->  ét forsøg / ét selvstændigt fund
  #### Historie|Statistik|Konklusion|Taktik  ->  de fire trin, foldbare
  @stat værdi :: forklaring                  ->  talkort (samles i et gitter)
"""

import html
import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "kapitler.md"
OUT = HERE / "index.html"

STONES = ["Historie", "Statistik", "Konklusion", "Taktik"]


# ---------------------------------------------------------------- hjælpere

def inline(text):
    """Markdown-inline -> HTML. Escaper først, formaterer derefter."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def slugify(text):
    text = re.sub(r"[^\wæøåÆØÅ\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")


# ---------------------------------------------------------------- blokrender

def render(lines, heading_base=1):
    """Renderer en klump linjer til HTML. Bruges til alle tekstområder."""
    out, i = [], 0
    n = len(lines)

    while i < n:
        line = lines[i]
        s = line.strip()

        if not s or s == "---":
            i += 1
            continue

        # Talkort — samles så længe der står @stat på linjerne i træk
        if s.startswith("@stat "):
            cards = []
            while i < n and lines[i].strip().startswith("@stat "):
                body = lines[i].strip()[len("@stat "):]
                value, _, label = body.partition("::")
                cards.append(
                    '<div class="stat"><div class="stat-v">%s</div>'
                    '<div class="stat-l">%s</div></div>'
                    % (inline(value.strip()), inline(label.strip())))
                i += 1
            out.append('<div class="stats">%s</div>' % "".join(cards))
            continue

        # Tabel
        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip()
                             for c in lines[i].strip().strip("|").split("|")])
                i += 1
            if len(rows) >= 2 and set(rows[1][0]) <= set("-: "):
                head, body = rows[0], rows[2:]
            else:
                head, body = None, rows
            out.append('<div class="tablewrap"><table>')
            if head:
                out.append("<thead><tr>%s</tr></thead>" % "".join(
                    "<th>%s</th>" % inline(c) for c in head))
            out.append("<tbody>")
            for r in body:
                out.append("<tr>%s</tr>" % "".join(
                    "<td>%s</td>" % inline(c) for c in r))
            out.append("</tbody></table></div>")
            continue

        # Overskrift
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            lvl = min(6, len(m.group(1)) + heading_base - 1)
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2)), lvl))
            i += 1
            continue

        # Citat — flere linjer i træk bliver til hver sin linje i blokken
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(inline(lines[i].strip().lstrip(">").strip()))
                i += 1
            out.append("<blockquote>%s</blockquote>"
                       % "<br>".join(b for b in buf if b))
            continue

        # Punktliste
        if re.match(r"^[-*]\s+", s):
            out.append("<ul>")
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                item = [lines[i].strip()[2:]]
                i += 1
                while (i < n and lines[i].strip()
                       and not re.match(r"^(#{1,6}\s|[-*]\s|\d+\.\s|>|\||@)",
                                        lines[i].strip())):
                    item.append(lines[i].strip())
                    i += 1
                out.append("<li>%s</li>" % inline(" ".join(item)))
            out.append("</ul>")
            continue

        # Nummereret liste
        if re.match(r"^\d+\.\s+", s):
            out.append("<ol>")
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                item = [re.sub(r"^\d+\.\s+", "", lines[i].strip())]
                i += 1
                while (i < n and lines[i].strip()
                       and not re.match(r"^(#{1,6}\s|[-*]\s|\d+\.\s|>|\||@)",
                                        lines[i].strip())):
                    item.append(lines[i].strip())
                    i += 1
                out.append("<li>%s</li>" % inline(" ".join(item)))
            out.append("</ol>")
            continue

        # Afsnit
        buf = []
        while (i < n and lines[i].strip() and lines[i].strip() != "---"
               and not re.match(r"^(#{1,6}\s|[-*]\s|\d+\.\s|>|\||@)",
                                lines[i].strip())):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf)))
        else:
            i += 1

    return "\n".join(out)


# ---------------------------------------------------------------- parser

def parse(md):
    """Deler dokumentet op i indledning, dele og kapitler."""
    preamble, parts = [], []
    chapter = block = stone = None
    part = None
    target = preamble

    for raw in md.split("\n"):
        s = raw.strip()

        m = re.match(r"^#\s+DEL\s+(.*)$", s)
        if m:
            part = {"title": m.group(1).strip(), "chapters": []}
            parts.append(part)
            chapter = block = stone = None
            target = None
            continue

        m = re.match(r"^##\s+(\d+)\.\s+(.*)$", s)
        if m:
            if part is None:
                part = {"title": None, "chapters": []}
                parts.append(part)
            chapter = {
                "num": m.group(1),
                "title": m.group(2).strip(),
                "slug": "kap-" + m.group(1),
                "princip": "",
                "side": "",
                "kern": [],
                "blocks": [],
            }
            part["chapters"].append(chapter)
            block = stone = None
            target = chapter["kern"]
            continue

        if chapter is not None:
            if s.startswith("@princip "):
                chapter["princip"] = s[len("@princip "):].strip()
                continue
            if s.startswith("@side "):
                chapter["side"] = s[len("@side "):].strip()
                continue

            m = re.match(r"^###\s+Blok\s*\d*\s*[·\-—.:]?\s*(.*)$", s)
            if m:
                block = {"title": m.group(1).strip(), "stones": []}
                chapter["blocks"].append(block)
                stone = None
                target = None
                continue

            m = re.match(r"^####\s+(.*)$", s)
            if m and block is not None:
                stone = {"label": m.group(1).strip(), "lines": []}
                block["stones"].append(stone)
                target = stone["lines"]
                continue

        if target is not None:
            target.append(raw)

    return preamble, parts


# ---------------------------------------------------------------- render side

def render_chapter(ch):
    parts = []
    meta = []
    if ch["princip"]:
        meta.append('<span class="chip">%s</span>' % inline(ch["princip"]))
    if ch["side"]:
        meta.append('<span class="src">%s</span>' % inline(ch["side"]))

    parts.append(
        '<section class="chapter" id="%s" data-princip="%s" '
        'data-title="%s">' % (
            ch["slug"], html.escape(ch["princip"], quote=True),
            html.escape("%s. %s" % (ch["num"], ch["title"]), quote=True)))
    parts.append(
        '<header class="ch-head"><span class="ch-num">%s</span>'
        '<div class="ch-title"><h3>%s</h3>%s</div></header>' % (
            ch["num"], inline(ch["title"]),
            '<p class="ch-meta">%s</p>' % "".join(meta) if meta else ""))

    kern = render(ch["kern"], heading_base=4)
    if kern:
        parts.append('<div class="kern">%s</div>' % kern)

    total = len(ch["blocks"])
    for idx, b in enumerate(ch["blocks"], 1):
        label = ("Blok %d af %d" % (idx, total)) if total > 1 else "Forsøget"
        parts.append('<article class="blok">')
        parts.append(
            '<header class="blok-head"><span class="blok-idx">%s</span>'
            '<h4>%s</h4></header>' % (label, inline(b["title"])))
        for st in b["stones"]:
            key = slugify(st["label"])
            parts.append(
                '<details class="stone s-%s" open>'
                '<summary><span class="arrow" aria-hidden="true"></span>'
                '<span class="stone-l">%s</span></summary>'
                '<div class="stone-b">%s</div></details>' % (
                    key, inline(st["label"]),
                    render(st["lines"], heading_base=5)))
        parts.append("</article>")

    parts.append("</section>")
    return "\n".join(parts)


def render_nav(parts):
    out = []
    for p in parts:
        if p["title"]:
            out.append('<p class="navdel">%s</p>' % html.escape(p["title"]))
        out.append("<ul>")
        for ch in p["chapters"]:
            out.append(
                '<li data-for="%s"><a href="#%s"><b>%s</b><span>%s</span></a>'
                '</li>' % (ch["slug"], ch["slug"], ch["num"],
                           html.escape(ch["title"])))
        out.append("</ul>")
    return "\n".join(out)


CSS = """
:root{
  --bg:#fbfaf8; --panel:#fff; --panel2:#f6f4f0; --ink:#17181b; --muted:#67635c;
  --line:#e4e0d9; --line2:#efece6; --accent:#8a2f1d; --accent-soft:#fbeee9;
  --historie:#8a5a2f; --statistik:#1d5c8a; --konklusion:#2f6b3c; --taktik:#6a3a80;
  --code:#f1eee8;
  --shadow:0 1px 2px rgba(0,0,0,.05),0 10px 30px rgba(0,0,0,.045);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme=light]){
    --bg:#121316; --panel:#191a1e; --panel2:#1f2126; --ink:#eae8e4; --muted:#a09c95;
    --line:#2b2e34; --line2:#232629; --accent:#e08a72; --accent-soft:#2a1d18;
    --historie:#d9a06b; --statistik:#79b6e6; --konklusion:#84c58e; --taktik:#c096da;
    --code:#23262b;
    --shadow:0 1px 2px rgba(0,0,0,.45),0 10px 30px rgba(0,0,0,.32);
  }
}
:root[data-theme=dark]{
  --bg:#121316; --panel:#191a1e; --panel2:#1f2126; --ink:#eae8e4; --muted:#a09c95;
  --line:#2b2e34; --line2:#232629; --accent:#e08a72; --accent-soft:#2a1d18;
  --historie:#d9a06b; --statistik:#79b6e6; --konklusion:#84c58e; --taktik:#c096da;
  --code:#23262b;
  --shadow:0 1px 2px rgba(0,0,0,.45),0 10px 30px rgba(0,0,0,.32);
}
*{box-sizing:border-box}
body{
  margin:0;background:var(--bg);color:var(--ink);
  font:17px/1.68 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
  -webkit-font-smoothing:antialiased;
}
.layout{display:grid;grid-template-columns:308px minmax(0,1fr);max-width:1340px;margin:0 auto}

/* ---- sidebar ---- */
#side{
  position:sticky;top:0;height:100vh;overflow-y:auto;padding:26px 20px 60px;
  border-right:1px solid var(--line);background:var(--panel)
}
#side h1{font-size:20px;line-height:1.25;margin:0 0 3px;letter-spacing:-.01em}
#side .sub{font-size:13px;color:var(--muted);margin:0 0 16px}
#q{
  width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:9px;
  background:var(--bg);color:var(--ink);font-size:14px;font-family:inherit
}
#q:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}
#filters{display:flex;flex-wrap:wrap;gap:6px;margin:11px 0 0}
#filters button{
  font:inherit;font-size:12px;padding:4px 10px;border-radius:999px;cursor:pointer;
  border:1px solid var(--line);background:var(--bg);color:var(--muted)
}
#filters button:hover{color:var(--accent);border-color:var(--accent)}
#filters button.on{background:var(--accent);border-color:var(--accent);color:#fff}
#foldall{
  width:100%;margin-top:10px;padding:8px 12px;border:1px solid var(--line);
  border-radius:9px;background:var(--bg);color:var(--muted);cursor:pointer;
  font:inherit;font-size:13px;text-align:left
}
#foldall:hover{color:var(--accent);border-color:var(--accent)}
.navdel{
  font-size:11.5px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
  color:var(--muted);margin:24px 0 7px
}
#side ul{list-style:none;margin:0;padding:0}
#side li a{
  display:flex;gap:9px;padding:6px 9px;border-radius:8px;text-decoration:none;
  color:var(--ink);font-size:14px;line-height:1.4
}
#side li a b{
  color:var(--muted);min-width:20px;font-variant-numeric:tabular-nums;font-weight:600
}
#side li a:hover{background:var(--accent-soft)}
#side li a:hover b{color:var(--accent)}
#side li.hide,.navdel.hide,.delhead.hide,#intro.hide{display:none}

/* ---- indhold ---- */
main{padding:44px 46px 140px;min-width:0}
#intro h1{font-size:36px;line-height:1.16;letter-spacing:-.022em;margin:0 0 16px}
#intro h2{font-size:22px;margin:44px 0 12px;letter-spacing:-.01em}
h2.delhead{
  margin:72px 0 8px;padding-top:24px;border-top:2px solid var(--line);
  font-size:13px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;
  color:var(--muted)
}
.chapter{
  background:var(--panel);border:1px solid var(--line);border-radius:16px;
  padding:28px 32px 30px;margin:22px 0;box-shadow:var(--shadow);scroll-margin-top:16px
}
.chapter.hide{display:none}
.ch-head{display:flex;gap:14px;align-items:flex-start;margin:0 0 16px}
.ch-num{
  flex:none;font-size:13px;font-weight:700;color:#fff;background:var(--accent);
  border-radius:8px;padding:4px 9px;line-height:1.45;font-variant-numeric:tabular-nums;
  margin-top:5px
}
.ch-title h3{font-size:25px;line-height:1.26;letter-spacing:-.017em;margin:0}
.ch-meta{margin:8px 0 0;display:flex;flex-wrap:wrap;gap:9px;align-items:center}
.chip{
  font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--accent);background:var(--accent-soft);border-radius:999px;padding:3px 10px
}
.src{font-size:12.5px;color:var(--muted)}
.kern{
  background:var(--panel2);border:1px solid var(--line2);border-left:3px solid var(--accent);
  border-radius:0 11px 11px 0;padding:15px 19px 1px;margin:0 0 6px;font-size:16px
}
.kern p{margin:0 0 14px}
.kern blockquote{margin:0 0 14px;padding:0;border:0;background:none;font:inherit}

/* ---- blok ---- */
.blok{margin:26px 0 0;padding:0 0 0 18px;border-left:2px solid var(--line)}
.blok-head{margin:0 0 4px}
.blok-idx{
  display:block;font-size:10.5px;font-weight:700;letter-spacing:.13em;
  text-transform:uppercase;color:var(--muted);margin-bottom:4px
}
.blok-head h4{font-size:19px;line-height:1.32;letter-spacing:-.012em;margin:0}

/* ---- de fire trin ---- */
details.stone{margin:16px 0 0;border-top:1px solid var(--line2)}
details.stone summary{
  list-style:none;cursor:pointer;user-select:none;
  display:flex;align-items:center;gap:9px;padding:11px 0 7px
}
details.stone summary::-webkit-details-marker{display:none}
details.stone summary::marker{content:""}
details.stone summary:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:5px}
.arrow{
  width:0;height:0;flex:none;border-left:5px solid var(--muted);
  border-top:4.5px solid transparent;border-bottom:4.5px solid transparent;
  transition:transform .18s ease
}
details.stone[open]>summary .arrow{transform:rotate(90deg)}
.stone-l{
  font-size:11.5px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;
  color:var(--muted)
}
.s-historie>summary .stone-l{color:var(--historie)}
.s-historie>summary .arrow{border-left-color:var(--historie)}
.s-statistik>summary .stone-l{color:var(--statistik)}
.s-statistik>summary .arrow{border-left-color:var(--statistik)}
.s-konklusion>summary .stone-l{color:var(--konklusion)}
.s-konklusion>summary .arrow{border-left-color:var(--konklusion)}
.s-taktik>summary .stone-l{color:var(--taktik)}
.s-taktik>summary .arrow{border-left-color:var(--taktik)}
details.stone summary:hover .stone-l{opacity:.72}
.stone-b>*:first-child{margin-top:0}
.stone-b>*:last-child{margin-bottom:6px}
.stone-b blockquote{
  margin:0 0 15px;padding:12px 16px;background:var(--panel2);
  border-left:3px solid var(--line);border-radius:0 9px 9px 0;
  font-size:15.5px;line-height:1.6
}

/* ---- talkort ---- */
.stats{
  display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));
  gap:10px;margin:0 0 17px
}
.stat{
  background:var(--panel2);border:1px solid var(--line2);border-radius:11px;
  padding:13px 15px 14px
}
.stat-v{
  font-size:25px;line-height:1.15;font-weight:700;letter-spacing:-.02em;
  color:var(--statistik);font-variant-numeric:tabular-nums;margin-bottom:5px
}
.stat-l{font-size:13.5px;line-height:1.48;color:var(--muted)}

p{margin:0 0 15px}
ul,ol{margin:0 0 15px;padding-left:23px}
li{margin:0 0 10px}
strong{font-weight:650}
em{font-style:italic}
code{background:var(--code);padding:1px 5px;border-radius:5px;font-size:.9em}
a{color:var(--accent)}
.tablewrap{overflow-x:auto;margin:0 0 20px;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:15px;min-width:420px}
th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line)}
th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
#toggle{
  position:fixed;right:16px;bottom:16px;z-index:20;width:42px;height:42px;
  border-radius:50%;border:1px solid var(--line);background:var(--panel);
  color:var(--ink);font-size:17px;cursor:pointer;box-shadow:var(--shadow)
}
#empty{display:none;color:var(--muted);padding:26px 0}
#empty.show{display:block}
@media (max-width:960px){
  .layout{grid-template-columns:1fr}
  #side{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line);padding:20px}
  #side nav{max-height:280px;overflow-y:auto;margin-top:6px}
  main{padding:26px 18px 100px}
  #intro h1{font-size:28px}
  .chapter{padding:22px 18px;border-radius:13px}
  .ch-title h3{font-size:21px}
  .blok{padding-left:13px}
  body{font-size:16px}
}
@media print{
  #side,#toggle{display:none}
  .layout{display:block}
  .chapter{break-inside:avoid;box-shadow:none;border:0;padding:0}
}
"""

JS = """
var q=document.getElementById('q'),
    chapters=[].slice.call(document.querySelectorAll('.chapter')),
    dels=[].slice.call(document.querySelectorAll('.delhead')),
    navdels=[].slice.call(document.querySelectorAll('.navdel')),
    intro=document.getElementById('intro'),
    empty=document.getElementById('empty'),
    navFor={},activeP='';
[].slice.call(document.querySelectorAll('#side li[data-for]')).forEach(function(li){
  navFor[li.dataset.for]=li;
});
chapters.forEach(function(c){c._txt=c.textContent.toLowerCase();});

function apply(){
  var v=q.value.trim().toLowerCase(),n=0;
  chapters.forEach(function(c){
    var hit=(!v||c._txt.indexOf(v)>-1)&&(!activeP||c.dataset.princip===activeP);
    c.classList.toggle('hide',!hit);
    var li=navFor[c.id]; if(li)li.classList.toggle('hide',!hit);
    if(hit)n++;
  });
  var filtering=!!v||!!activeP;
  intro.classList.toggle('hide',filtering);
  dels.forEach(function(h){
    var any=false,el=h.nextElementSibling;
    while(el&&!el.classList.contains('delhead')){
      if(el.classList.contains('chapter')&&!el.classList.contains('hide'))any=true;
      el=el.nextElementSibling;
    }
    h.classList.toggle('hide',filtering&&!any);
  });
  navdels.forEach(function(p){
    var ul=p.nextElementSibling,any=false;
    if(ul)[].slice.call(ul.children).forEach(function(li){
      if(!li.classList.contains('hide'))any=true;
    });
    p.classList.toggle('hide',filtering&&!any);
  });
  empty.classList.toggle('show',filtering&&n===0);
  if(v){stones.forEach(function(d){d.open=true;});}
  else applyFold(collapsed);
}
q.addEventListener('input',function(){apply();if(q.value)window.scrollTo(0,0);});
[].slice.call(document.querySelectorAll('#filters button')).forEach(function(b){
  b.addEventListener('click',function(){
    activeP=(activeP===b.dataset.p)?'':b.dataset.p;
    [].slice.call(document.querySelectorAll('#filters button')).forEach(function(x){
      x.classList.toggle('on',x.dataset.p===activeP);
    });
    apply();window.scrollTo(0,0);
  });
});

var stones=[].slice.call(document.querySelectorAll('details.stone')),
    foldBtn=document.getElementById('foldall'),collapsed=false;
try{collapsed=localStorage.getItem('jafold')==='1';}catch(e){}
function applyFold(c){
  stones.forEach(function(d){d.open=!c;});
  foldBtn.textContent=c?'\\u25B8  Fold alle trin ud':'\\u25BE  Fold alle trin sammen';
}
applyFold(collapsed);
foldBtn.addEventListener('click',function(){
  collapsed=!collapsed;
  try{localStorage.setItem('jafold',collapsed?'1':'0');}catch(e){}
  applyFold(collapsed);
});
window.addEventListener('beforeprint',function(){
  stones.forEach(function(d){d._was=d.open;d.open=true;});
});
window.addEventListener('afterprint',function(){
  stones.forEach(function(d){d.open=d._was;});
});

var t=document.getElementById('toggle'),root=document.documentElement;
function cur(){
  return root.getAttribute('data-theme')
      ||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
}
function paint(){t.textContent=cur()==='dark'?'\\u2600':'\\u263D';}
try{var s=localStorage.getItem('jatheme');if(s)root.setAttribute('data-theme',s);}catch(e){}
paint();
t.addEventListener('click',function(){
  var nw=cur()==='dark'?'light':'dark';
  root.setAttribute('data-theme',nw);
  try{localStorage.setItem('jatheme',nw);}catch(e){}
  paint();
});
"""


def main():
    preamble, parts = parse(SRC.read_text(encoding="utf-8"))

    chapters = [c for p in parts for c in p["chapters"]]
    blocks = sum(len(c["blocks"]) for c in chapters)
    principper = []
    for c in chapters:
        if c["princip"] and c["princip"] not in principper:
            principper.append(c["princip"])

    body = []
    for p in parts:
        if p["title"]:
            body.append('<h2 class="delhead" id="%s">DEL %s</h2>'
                        % (slugify(p["title"]), inline(p["title"])))
        for c in p["chapters"]:
            body.append(render_chapter(c))

    filters = "".join(
        '<button type="button" data-p="%s">%s</button>'
        % (html.escape(p, quote=True), html.escape(p)) for p in principper)

    page = """<!doctype html>
<html lang="da"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>JA! — 50 videnskabeligt beviste veje til at overbevise</title>
<meta name="description" content="Alle kapitler fra Goldstein, Martin og Cialdinis Yes!, skåret op i historie, statistik, konklusion og taktik.">
<meta name="color-scheme" content="light dark">
<style>%s</style>
</head><body>
<div class="layout">
<aside id="side">
  <h1>JA!</h1>
  <p class="sub">%d kapitler · %d forsøg</p>
  <input id="q" type="search" placeholder="Søg i kapitlerne…" aria-label="Søg">
  <div id="filters">%s</div>
  <button id="foldall" type="button"></button>
  <nav>%s</nav>
</aside>
<main>
<div id="intro">
%s
</div>
%s
<p id="empty">Ingen kapitler matcher søgningen.</p>
</main>
</div>
<button id="toggle" title="Skift tema" aria-label="Skift lyst/mørkt tema">&#9790;</button>
<script>%s</script>
</body></html>
""" % (CSS, len(chapters), blocks, filters, render_nav(parts),
       render(preamble), "\n".join(body), JS)

    OUT.write_text(page, encoding="utf-8")
    print("index.html bygget: %d kapitler, %d blokke, %d KB"
          % (len(chapters), blocks, len(page) // 1024))


if __name__ == "__main__":
    main()
