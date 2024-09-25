# Informační systémy (IIS) - Zvířecí útulek 🐻‍❄️

>Zadání není finální.

Úkolem zadání je vytvořit jednoduchý informační systém pro evidenci opuštěných zvířat zvířecím útulkem (např. králíků, koček nebo psů) a možnost jejich zapůjčení a venčení dobrovolníky.

Každé zvíře je identifikováno jménem, druhem a dalšími vhodně zvolenými atributy (např. věk, fotky, případně se inspirujte např. popisem zvířat pana Zdeňka Srstky, apod.). Zvíře má dále svoji historii (např. informace o nalezení) a evidenci svého zdravotního stavu (např. informace o očkování) a průběžných prohlídkách veterinářem. Zvíře je možné přidat do rozvrhu pro možné venčení.

Ověření dobrovolníci mohou tyto zvířata vyhledávat a provádět rezervace pro jejich zapůjčení dle volných termínů v rozvrhu.

---

>Konkrétně budou v systému vystupovat následující role:

#### *Administrátor:*
- Spravuje uživatele, jako jediný vytváří pečovatele a veterináře.

#### *Pečovatel:*
- Spravuje zvířata, vede jejich evidenci.
- Vytváří rozvrhy pro venčení.
- Ověřuje dobrovolníky.
- Schvaluje rezervace zvířat na venčení, eviduje zapůjčení a vrácení.
- Vytváří požadavky na veterináře.

#### *Veterinář:*
- Vyřizuje požadavky od pečovatele (plánuje vyšetření zvířat dle požadavků).
- Udržuje zdravotní záznamy zvířat.

#### *Dobrovolník:*
- Rezervuje zvířata na venčení.
- Vidí historii svých venčení.

#### *Neregistrovaný uživatel:*
- Prochází informace o útulku a zvířatech.

---

### Náměty na možná rozšíření:
- Sestavování plánu pro medikaci léků zvířatům.
- Dle vlastní fantazie, popište v dokumentaci…

---

## Rozjetí projektu
Vyzkoušeno na Windows 11, jelikož na WSLku nelze rozjet Apache (ani jiný) web server.

### Postup
- 1. Stažení XAMPP: https://sourceforge.net/projects/xampp/files/XAMPP%20Windows/8.1.25/xampp-windows-x64-8.1.25-0-VS16-installer.exe
- 2. Stažení Composer: https://getcomposer.org/Composer-Setup.exe
- 3. Sync lokálního repa s remote origin/master
- 4. Spuštění serveru v CMD projektu:
    ```
     php artisan serve
    ```
