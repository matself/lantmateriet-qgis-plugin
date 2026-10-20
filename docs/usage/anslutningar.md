# Anslutningar till tjänster

Knappen _Lägg till tjänster i Datakällor_ i pluginets inställningar skapar färdiga anslutningar i QGIS datakällor
(Browser-panelen och Datakällshanteraren). Anslutningarna använder den autentisering du har valt i inställningarna,
så du behöver inte ange URL eller åtkomstnycklar själv.

## Vilka anslutningar skapas

Du väljer själv vilka av dem som ska läggas till.

| Anslutning                    | Typ                  | Innehåll                                  |
|-------------------------------|----------------------|-------------------------------------------|
| Ortofoton Nedladdning         | STAC                 | Nedladdning av ortofoton                  |
| Markhöjdmodell Nedladdning    | STAC                 | Nedladdning av höjddata                   |
| NGP Detaljplan                | STAC                 | Detaljplaner                              |
| NGP Byggnad                   | STAC                 | Byggnader                                 |
| NGP Kulturhistorisk lämning   | STAC                 | Kulturhistoriska lämningar                |
| NGP Gräns för fjällnära skog  | STAC                 | Gräns för fjällnära skog                  |
| Fastighetsindelning Direkt    | OGC API Features     | Registerenhetsområden (ytor, linjer, punkter) |

Anslutningar till Ortofoton, Markhöjdmodell och Fastighetsindelning kräver att din applikation i Lantmäteriets
API-manager prenumererar på respektive API, se [åtkomstnycklar](installningar/atkomstnycklar.md).

## Vad pluginet gör, och inte gör

Pluginet skapar enbart anslutningarna. Det är QGIS som sedan visar kataloger, objekt och sökmöjligheter, och vad som
finns där beror på vilken version av QGIS du använder.

Pluginet har ingen egen kartvy för att peka ut ett område och se vilka ortofoto- eller höjdrutor som täcker det. En
STAC-katalog för hela Sverige innehåller mycket stora mängder objekt, och listan i Browser-panelen visar inte var på
kartan varje objekt finns.

Om du vill ladda ned data för ett avgränsat område:

* För **adresser och fastigheter** finns [algoritmer](algoritmer/index.md) som hämtar data inom ett valt område eller
  inom polygoner i ett lager.
* För **fastighetsindelning** kan du lägga till anslutningen _Fastighetsindelning Direkt_ som ett vanligt lager och
  zooma till området, då hämtas bara det som syns.
* För **ortofoton och höjddata** gäller QGIS egna sökmöjligheter för STAC, se
  [QGIS dokumentation](https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/index.html).

## Felsökning

* **Forbidden eller "Resource forbidden"**: applikationen saknar prenumeration på API:et. Klicka på _Verifiera
  konfiguration_ i inställningarna, det visar vilka API:er som saknas.
* **Tom lista eller felmeddelande direkt efter att anslutningen lagts till**: kontrollera att autentiseringen är vald och
  att inställningarna är sparade.
