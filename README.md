# JA! — 50 videnskabeligt beviste veje til at overbevise

**Publiceret:** https://nikolai-cnm.github.io/cialdini-ja/

Alle kapitler fra Noah J. Goldstein, Steve J. Martin og Robert B. Cialdinis
*Yes! 50 Scientifically Proven Ways to Be Persuasive* (Free Press, 2008),
skåret op i de forsøg, de faktisk bygger på.

**Status: komplet.** Alle 50 kapitler, 94 blokke, 221 talkort og 62 ordrette citater.

## Opbygning

Hvert kapitel består af én eller flere **blokke** — én pr. forsøg eller pr.
selvstændigt fund i kapitlet. Hver blok har fire trin:

| Trin | Indhold |
|---|---|
| **Historie** | Hvad skete der, hvem gjorde det, hvordan var forsøget sat op |
| **Statistik** | De faktiske tal fra studiet — intet rundet opad, intet opfundet |
| **Konklusion** | Hvad tallene betyder, og hvilket princip der er på spil |
| **Taktik** | Hvordan det bruges i salg, ledelse, marketing, forhandling og privatliv |

Antallet af blokke følger bogen, ikke en skabelon. **Reglen:** der er en ny blok,
hvor bogen drager en ny konklusion og giver et nyt råd. 15 kapitler har én blok,
26 har to, 9 har tre.

Kapitel 5 har tre, fordi bogen dér stiller tre studier op mod hinanden og pointen
først ligger i sammenstillingen. Kapitel 11 har én, selv om pastil-forsøget har tre
betingelser, fordi bogen drager én samlet konklusion af dem.

De 50 kapitler er grupperet i 14 dele og mærket med 12 principper, der kan filtreres
på i sidebaren: Cialdinis seks (social proof, gengældelse, konsistens, knaphed,
sympati, autoritet) plus seks mekanismer, der falder uden for dem.

**33 steder gengiver bogen ingen tal** — kun retningen af et resultat. Der står en
`@note` hvert sted i stedet for tal hentet andetsteds fra.

## Filer

| Fil | Rolle |
|---|---|
| `kapitler.md` | **Kilden.** Al tekst redigeres her |
| `build.py` | Bygger `index.html` ud fra `kapitler.md` |
| `kontrol.py` | Kontroltest: holder alle tal og citater op mod bogen |
| `artifact.html` | Genereret. Samme side uden html/head-wrapper |
| `index.html` | Genereret. **Redigér den aldrig direkte** |
| `kilde/` | Bogteksten som OCR, en fil pr. side. **Uden for git** |

```bash
python3 kontrol.py   # skal give "0 med afvigelser" før build
python3 build.py
```

## Kontroltest

`kontrol.py` trækker hvert `@stat`-tal og hver engelsk original ud af
`kapitler.md` og slår dem op i bogens egen tekst. Exit 0 betyder, at alt blev
fundet. Kør den før hvert build.

Kilden ligger i `kilde/` og er holdt uden for git — bogteksten er
ophavsretligt beskyttet. Genskab den sådan:

```bash
pdftoppm -r 300 -gray -png BOGEN.pdf img/p
for f in img/p-*.png; do tesseract "$f" "${f%.png}" -l eng --psm 6; done
mkdir kilde && cp img/*.txt kilde/
```

**OCR kan selv tage fejl.** Slår testen ud på et tal, så se på sidebilledet,
før du retter teksten. Bogens gamle 5-tal blev fx læst som 9 i to uafhængige
OCR-gennemløb — valgmarginen i kapitel 16 er 537 stemmer, ikke 937.

Tal, der er vores egen udregning og ikke står i bogen, markeres med ordet
"udregning" i `@stat`-labelen og springes over af testen.

## Markdown-dialekt

```markdown
# DEL 1 — Social proof: flokkens bevis     <- gruppe i navigationen

## 1. Kapiteloverskriften                   <- nyt kapitel
@princip Social proof                       <- mærkat, kan filtreres på
@side Kapitel 1 · s. 9–14                   <- kildehenvisning

> **Kernen:** Den ene sætning, kapitlet koger ned til.

### Blok 1 · Titel på forsøget

#### Historie
Fri tekst, lister, citater.

#### Statistik
@stat +26 % :: hvad tallet dækker over
@stat 0 :: endnu et talkort

#### Konklusion
...

#### Taktik
1. Nummereret liste med handlingsanvisninger.
```

`@stat`-linjer, der står i træk, samles automatisk i et gitter af talkort.

### Meta ads — kurateret genvej

Forrest på siden ligger en sektion med de 15 kapitler, der oversætter sig
direkte til en Meta-annonce: ét fra hver af de 14 dele plus den dyreste fejl.

```markdown
# META Meta ads — de 15, du kan lægge direkte ned over en annonce

### AD 1 · Sig, hvad flertallet allerede gør — i første linje
@stat +26 % :: flere deltog, da beskeden fortalte, hvad flertallet gjorde
Fri tekst om hvorfor det virker på Meta.
@ads Svag åbning :: ...
@ads Stærk åbning :: ...
```

Kapitlerne bliver **ikke** flyttet eller kopieret. Hvert kort henter titel og
princip fra selve kapitlet og linker til det, så de to aldrig kan komme ud af
trit — der er kun én kilde til teksten.

`@ads` er **vores egne** annonceeksempler og ser bevidst anderledes ud end
`@citat`, som er bogens ord. De to må ikke kunne forveksles på siden.
Kontroltesten kontrollerer `@stat`-tallene i sektionen på lige fod med
kapitlernes, men rører ikke `@ads`.

### Ordrette citater

```markdown
@citat Før :: Operatørerne venter, ring nu. :: Operators are waiting, please call now.
@citat Efter :: Hvis operatørerne er optaget, så ring venligst igen. :: If operators are busy, please call again.

@note Bogen citerer ikke skiltets ordlyd — derfor står den uden anførselstegn.
```

**Regel:** ændrer bogen en konkret formulering, skal den stå ordret — som `@citat`,
med den engelske original i tredje felt, så oversættelsen kan efterprøves.
Refererer bogen kun en ordlyd uden at citere den, står den uden anførselstegn
og med et `@note` om hvorfor. Bogens hotelskilte i kapitel 1 er det første
tilfælde: de citeres aldrig ordret, og så gør siden det heller ikke.

## Siden

Én selvstændig HTML-fil uden eksterne assets. Søgning, filtrering på princip,
foldbare trin, lyst/mørkt tema, printvenlig. Klar til GitHub Pages —
`index.html` ligger i roden.

## Kilde

Goldstein, N. J., Martin, S. J. & Cialdini, R. B. (2008).
*Yes! 50 Scientifically Proven Ways to Be Persuasive.* New York: Free Press.

Tal og forsøgsbeskrivelser er hentet direkte fra bogen. Citater holdes korte.
Længere passager gengives ikke.
