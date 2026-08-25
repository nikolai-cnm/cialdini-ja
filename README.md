# JA! — 50 videnskabeligt beviste veje til at overbevise

**Publiceret:** https://nikolai-cnm.github.io/cialdini-ja/

Alle kapitler fra Noah J. Goldstein, Steve J. Martin og Robert B. Cialdinis
*Yes! 50 Scientifically Proven Ways to Be Persuasive* (Free Press, 2008),
skåret op i de forsøg, de faktisk bygger på.

**Status: pilot.** Kapitel 1–5 er færdige. De øvrige 45 følger samme skabelon.

## Opbygning

Hvert kapitel består af én eller flere **blokke** — én pr. forsøg eller pr.
selvstændigt fund i kapitlet. Hver blok har fire trin:

| Trin | Indhold |
|---|---|
| **Historie** | Hvad skete der, hvem gjorde det, hvordan var forsøget sat op |
| **Statistik** | De faktiske tal fra studiet — intet rundet opad, intet opfundet |
| **Konklusion** | Hvad tallene betyder, og hvilket princip der er på spil |
| **Taktik** | Hvordan det bruges i salg, ledelse, marketing, forhandling og privatliv |

Kapitel 1, 3 og 4 har to blokke. Kapitel 5 har tre. Kapitel 2 har én.
Antallet følger bogen — ikke en skabelon.

## Filer

| Fil | Rolle |
|---|---|
| `kapitler.md` | **Kilden.** Al tekst redigeres her |
| `build.py` | Bygger `index.html` ud fra `kapitler.md` |
| `index.html` | Genereret. **Redigér den aldrig direkte** |

```bash
python3 build.py
```

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
