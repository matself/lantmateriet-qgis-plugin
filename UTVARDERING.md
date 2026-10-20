# Utvärdering av lantmateriet-qgis-plugin

Underlag: koden i `main` vid commit `20e9f41` (2026-10-20), granskad tillsammans med
en körning i QGIS 4.2.3 (Windows) och anrop mot Lantmäteriets produktions-API.
Det som anges som verifierat har jag testat. Det som anges som antagande har jag inte kunnat bekräfta.

## Sammanfattning

Pluginet fungerar i grunden, men är skört och sitter ihop på ett ovanligt sätt. Det går att
publicera efter städningen i 1.0.2. De största riskerna är Python-versionskravet, de hårdkodade
API-versionerna och att scopes och prenumerationer hanteras av användaren i stället för av pluginet.

Läget i `main` jämfört med upstream (`qgissverige/lantmateriet-qgis-plugin`): forken ligger sex commits
före och noll efter (kontrollerat med `git rev-list` mot `upstream/main`). Upstream har inte ändrats sedan v1.0.1 (2025-09-26).

## Omfattning

| Del | Omfattning |
|---|---|
| Kod i `lantmateriet_qgis/` | ca 5 500 rader Python |
| Tester | 67 enhetstester (körs utan QGIS), plus QGIS-tester som inte kan köras lokalt eller i CI |
| Dokumentation | svensk användarhandledning (mkdocs), README på engelska med gränssnittsavsnitt |
| Funktioner | inställningssida, tre sökfilter, fyra Processing-algoritmer, uttrycksfunktioner, STAC- och OGC-anslutningar |

## Verifierat

* Alla 67 enhetstester går igenom.
* Bandit och detect-secrets är rena. Flake8 är rent med `.flake8` i pluginroten.
* Pluginet laddas i QGIS 4.2.3, algoritmerna och providern registreras.
* Adresstjänsten (Belägenhetsadress Direkt) svarar med riktiga data. Övriga Direkt-tjänster kunde inte
  testas, eftersom den applikation jag testade med saknar prenumeration på dem.
* STAC-tjänsterna `stac-vektor`, `stac-bild` och `stac-hojd` svarar 200.
* Token-endpointen byter tyst ut scopes som applikationen inte prenumererar på mot `default`.
  Pluginet kontrollerar nu detta vid _Verifiera konfiguration_.

## Risker och problem

Sorterade efter hur allvarliga jag bedömer dem.

### 1. Python-versionen räcker inte för det som metadata utlovar

Koden använder `typing.Self` (Python 3.11) i `locators/address.py`, `locators/property.py`,
`locators/gemensamhetsanlaggning.py` och `core/settings.py`, samt `X | Y` i typannoteringar
(Python 3.10). Samtidigt anger `metadata.txt` `qgisMinimumVersion=3.34`, och både ruff
(`target-version = "py39"`) och CI (`PYTHON_VERSION: 3.9`) utgår från Python 3.9.

Konsekvens (antagande): på en QGIS 3.34 som levereras med Python äldre än 3.11 går inte pluginet att
ladda. Vilken Python som följer med varje QGIS-version och plattform har jag inte kontrollerat.
Antingen bör `qgisMinimumVersion` höjas till den första version som garanterat har Python 3.11,
eller så bör `Self` ersättas (till exempel med `typing_extensions` eller en vanlig typannotering).
Ruff- och CI-inställningarna bör följa det som väljs.

### 2. API-versioner är hårdkodade och kan vara på väg att avvecklas

`belagenhetsadress/v4.2`, `fastighetsamfallighet/v3.1`, `gemensamhetsanlaggning/v2.1` och
`registerbeteckning/v5` ligger som strängar i varje klient. Mitt test visade att
`belagenhetsadress/v5` och `registerbeteckning/v6` också svarar (401, alltså finns), så nyare
versioner är troligen släppta. Jag har inte kontrollerat avvecklingsdatum. Scope-namnen i
`Settings.required_scopes()` följer samma versionsnummer och måste ändras tillsammans med dem.

### 3. Scopes och prenumerationer hanteras av användaren

Autentiseringen är en vanlig QGIS OAuth2-konfiguration som användaren skapar. Pluginet frågar om det
får lägga till scopes i den vid sparande. Saknas prenumerationen på ett API får användaren
Forbidden utan förklaring, tills nu då _Verifiera konfiguration_ pekar ut vilka API:er som saknas.
Det här är en konsekvens av hur Lantmäteriets API-manager fungerar, men fler delar av flödet än
nödvändigt ligger på användaren.

### 4. Livscykeln (laddning och avladdning) är sårbar

Fel i `unload()` vid omladdning rättades i 20e9f41: providern ägs av Processing-registret och kunde
redan vara raderad. `unload()` har fortfarande tre olika avregistreringsmönster (inställningssida,
sökfilter, provider) och inga tester. Själva omladdningen har jag inte kunnat verifiera i en ren
QGIS-session.

### 5. QGIS-tester körs inte

`tester.yml` har jobbet `test-qgis` med `if: false` och en QGIS 3.28-container. `tests/qgis/`
(autentisering och inställningar) går därför varken att köra lokalt med systemets Python eller i CI.
Det gäller också de nya delar jag har lagt till (kontrollen av prenumerationer använder bara
rena funktioner i testerna, själva nätverksanropet är inte testat automatiskt).

### 6. Struktur och namngivning

* Klientfilerna upprepar mycket (sökning på text, geometri och beteckning) utan gemensam bas utöver
  `BaseClient` för HTTP.
* Domän- och API-termer är svenska (`registerenhetsomrade`, `faststalltNamn`) medan koden i övrigt är
  engelsk. Det är rimligt för API-fält men gör att klass- och funktionsnamn blandar språk
  (`FastighetOchSamfallighetDirektClient`).
* Funktionerna lever på fyra ställen (inställningssida, sökfilter, Processing, uttryck) utan någon
  gemensam ingång. Pluginet har inga menyposter eller verktygsfält.
* `download_properties.py` innehåller två kommenterade kodblock och två TODO-kommentarer om att flera
  objekt ger felmeddelanden vid inläsning.
* HTML-hjälptexterna för uttrycksfunktionerna är långa strängar i `core/functions/*.py` (flake8
  E501 är avstängt för dem).

### 7. Språk för plugins.qgis.org

Alla förklaringar är på engelska, men gränssnittet är på svenska. README har ett engelskt avsnitt som
förklarar det. Kontrollskriptet flaggar fortfarande svenska produktnamn i docstrings, vilket är
egennamn och får stå kvar.

## Gjort under städningen (1.0.2)

* Pluginets namn ändrat till `Lantmäteriet Services`, engelsk `about`, ifylld `changelog`, licens och taggar.
* Flake8-rent, `.flake8` tillagd, långa rader brutna, svensk TODO översatt.
* Varning vid saknad API-prenumeration i _Verifiera konfiguration_ (10 nya tester).
* Rättning av fel vid omladdning av pluginet.
* README: engelskt avsnitt `User interface`. Handledning: ny sida om anslutningar.
* Installerbar zip byggs från `HEAD` med `LICENSE` i pluginroten.

## Rekommendationer

1. Bestäm lägsta Python-version och rätta `qgisMinimumVersion`, `ruff` och CI därefter (punkt 1).
2. Kontrollera Lantmäteriets avvecklingsplan för de fyra API-versionerna och samla versionsnummer
   och scope-namn på ett ställe (punkt 2).
3. Aktivera QGIS-testerna i CI eller flytta ut så mycket logik som möjligt i rena funktioner som de 67
   enhetstesterna redan täcker (punkt 5).
4. Gör en ren omladdningskontroll i QGIS 4 och 3.40 efter en nystart (punkt 4).
5. Överväg en menypost eller liknande ingång. Det är ett beslut om vad pluginet ska vara, inte ett fel.

## Det jag inte har gjort eller kunnat kontrollera

* Ingen uppladdning till plugins.qgis.org, ingen tagg eller release.
* Test mot QGIS 3.x. Allt körande test gjordes i QGIS 4.2.3.
* Nedladdningsalgoritmerna och sökfiltren mot riktiga data (autentiseringen jag testade med saknade
  scopes, och prenumerationerna finns bara för adress).
* Att den publicerade handledningen på GitHub Pages motsvarar `docs/` i `main`.
