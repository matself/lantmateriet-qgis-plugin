# Ändringslogg

Detta format är baserat på [Keep a Changelog](https://keepachangelog.com/sv/) och detta projekt använder sig av [Semantic Versioning](https://semver.org/).

## 1.0.2 - 2026-10-20

* Korrigera krasch (`AttributeError: 'NoneType' object has no attribute 'split'`) när
  inställningar sparas och den valda autentiseringen saknar scopes
* Korrigera krasch när den valda autentiseringen har tagits bort eller inte är av typen OAuth2
* Undvik inledande blanksteg i scope-listan när scopes läggs till
* Korrigera URL för NGP Kulturhistorisk lämning
* Pluginets namn är nu `Lantmäteriet Services`
* Varna vid verifiering av konfigurationen om applikationen saknar prenumeration på valda Direkt-tjänster i API-managern

## 1.0.1 - 2025-09-26

* Korrigera fel vid loggning av nätverksfel vid sökning
* Loggning för inläsning/uppdatering av inställningar
* Bättre hantering av egna URLer

## 1.0.0 - 2025-06-30

* Första publika version

## 0.1.0 - 2025-05-07

* Förhandsrelease till testare

### Nytt

* Sökfunktion för adresser, fastigheter, samfälligheter och gemensamhetsanläggningar
* Verktyg för nedladdning av adresser respektive fastigheter och samfälligheter
* Funktioner för användning i uttryck för fastighets- och adressinformation
* Smidig konfiguration av anslutning till Lantmäteriet
* Enkelt att lägga till tjänster från Lantmäteriet som datakällor
