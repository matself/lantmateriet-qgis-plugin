<div align="center">

<img src="docs/logo.svg" width="100px" />

</div>

# QGIS Plugin for Lantmäteriets services

This is a QGIS plugin that provides a convenient connection to several of Lantmäteriet's (the national land survey of Sweden) services, such as downloading data, connecting to STAC endpoints, and searching using the locator.

<div align="center">

[Snabbstart](https://qgissverige.github.io/lantmateriet-qgis-plugin/usage/snabbstart/) &bullet; [Usage](https://qgissverige.github.io/lantmateriet-qgis-plugin/usage/) &bullet; [Development](https://qgissverige.github.io/lantmateriet-qgis-plugin/development/contribute/)

</div>

## Features

* Search for addresses and properties using the locator
* Download data using the processing toolbox
* Automatically at service connections to the Browser
* Access data from expressions

## User interface

The user interface is in Swedish. This section explains it in English. The full user documentation (in Swedish) is at <https://qgissverige.github.io/lantmateriet-qgis-plugin>.

All services require credentials from Lantmäteriet's API Manager (a free account and an application, giving a Consumer Key and a Consumer Secret).

### Settings dialog ("Lantmäteriet - Settings")

Opened from the QGIS settings dialog. It configures the authentication and adds service connections to the QGIS Browser.

| Swedish label | English meaning | What it does |
|---|---|---|
| Ange åtkomstnycklar | Enter access keys | Opens a dialog where the Consumer Key and Consumer Secret are entered and stored as an OAuth2 authentication configuration |
| Consumer Key / Consumer Secret | Consumer Key / Consumer Secret | The credentials from Lantmäteriet's API Manager |
| Verifiera konfiguration | Verify configuration | Tests the credentials against the selected environment |
| Lantmäteriets produktionsmiljö | Lantmäteriet's production environment | Use the production services (default) |
| Lantmäteriets verifikationsmiljö | Lantmäteriet's verification (test) environment | Use the verification services |
| Egen URL | Custom URL | Use a custom base URL for the services |
| Tjänster | Services | List of the Lantmäteriet services that can be added as connections |
| Lägg till tjänster i Datakällor | Add services to Data Sources | Adds the selected services as connections in the QGIS Browser |
| Markhöjdmodell Nedladdning | Elevation model download | STAC service for downloading elevation data |
| Ortofoton Nedladdning | Orthophoto download | STAC service for downloading orthophotos |
| Fastighetsindelning Direkt | Property division (direct) | OGC API Features service for property boundaries |
| Belägenhetsadress Direkt, Fastighet och Samfällighet Direkt, Gemensamhetsanläggning Direkt, Registerbeteckning Direkt | Address, Property and common property, Joint facility and Property designation (direct) services | The API products used by the locator and the download algorithms |
| Nationella geodataplattformen | National geodata platform | STAC services from the national geodata platform (NGP) |
| Övriga tjänster | Other services | Additional services |
| Spara tjänster | Save services | Confirmation dialog title when saving connections |

### Locator (search bar)

Type a prefix, a space and a search text in the QGIS locator bar.

| Prefix | Swedish name | English meaning | What it finds |
|---|---|---|---|
| `adr` | Adresser | Addresses | Addresses by street name and number |
| `fgh` | Fastighetsregistret | Property register | Properties and common properties by designation (e.g. `Kommun Trakt 1:1`) |
| `gan` | Gemensamhetsanläggningar | Joint facilities | Joint facilities by designation |

### Processing algorithms (provider "Lantmäteriet Services")

| Swedish name | English meaning | What it does |
|---|---|---|
| Hämta adresser inom polygoner | Download addresses within polygons | Downloads all addresses inside the polygons of an input layer into a point layer |
| Hämta adresser inom ett område | Download addresses within an extent | Downloads all addresses inside a given extent |
| Hämta fastigheter och samfälligheter inom polygoner | Download properties and common properties within polygons | Downloads properties and common properties inside the input polygons into polygon, line and point layers |
| Hämta fastigheter och samfälligheter inom ett område | Download properties and common properties within an extent | The same, for a given extent |

### Messages

| Swedish message | English meaning | When it appears |
|---|---|---|
| Hittade ett outrett område i svaret från Lantmäteriet. Detta kommer inte inkluderas i nedladdningen. | Found an unresolved area in the response from Lantmäteriet. It will not be included in the download. | A property download returns an area without usable geometry |

## Sponsors

The development of this plugin was made possible by:

| QGIS Sverige                                                   | Sweco Sverige AB                                        | Kristianstads kommun                                           |
|----------------------------------------------------------------|---------------------------------------------------------|----------------------------------------------------------------|
| <img width="1000" src="docs/bidragsgivare-qgis-sverige.png" /> | <img width="1000" src="docs/bidragsgivare-sweco.svg" /> | <img width="1000" src="docs/bidragsgivare-kristianstad.png" /> |

## License

Distributed under the terms of the [`GPLv2+` license](LICENSE).
