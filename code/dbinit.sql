-- MySQL databáze pro IIS projekt, jehož zadáním je "Zvířecí útulek"

-- pozn.    VARCHAR2 a NVARCHAR/NVARCHAR2 ve v MySQL nepoužívají
--          používám VARCHAR(255) - VARCHAR může mít proměnlivou délku

-----------------------------------------------------------------------------------------------
----------------------------------------- DROP TABLE ------------------------------------------
-----------------------------------------------------------------------------------------------

DROP TABLE IF EXISTS Zvire;
DROP TABLE IF EXISTS Plemeno;
DROP TABLE IF EXISTS Zdravotni_zaznam;
DROP TABLE IF EXISTS Fotka_zvirete;

DROP TABLE IF EXISTS Uzivatel;
DROP TABLE IF EXISTS Veterinar;
DROP TABLE IF EXISTS Administrator;
DROP TABLE IF EXISTS Dobrovolnik;
DROP TABLE IF EXISTS Pecovatel;

DROP TABLE IF EXISTS Prohlidka;
DROP TABLE IF EXISTS Venceni;
DROP TABLE IF EXISTS Rezervace;

-----------------------------------------------------------------------------------------------
---------------------------------------- CREATE TABLE -----------------------------------------
-----------------------------------------------------------------------------------------------

CREATE TABLE Zvire (
    ID_zvirete INT AUTO_INCREMENT not NULL,
    Druh VARCHAR(255) not NULL,
    Jmeno VARCHAR(255) not NULL,
    Pohlavi TINYINT not NULL, -- 0 = samec(muž), 1 = samice(žena)
    Datum_narozeni DATE, -- může být NULL, nevíme kdy se zvíře narodilo a jeho věk
    Datum_prichodu DATE not NULL,
    Aktivni BOOLEAN not NULL, -- false = není v útulku, true = je v útulku
    Popis TEXT not NULL,

    PRIMARY KEY(ID_zvirete),

    ID_plemene INT, -- cizí klíč na tabulku Plemeno
    FOREIGN KEY(ID_plemene) REFERENCES Plemeno(ID_plemene) -- Vazba na Plemeno
);

CREATE TABLE Plemeno (
    ID_plemene INT AUTO_INCREMENT not NULL,
    Nazev VARCHAR(255) not NULL,

    PRIMARY KEY(ID_plemene)
);

CREATE TABLE Zdravotni_zaznam (
    ID_zaznamu INT AUTO_INCREMENT not NULL,
    Nazev VARCHAR(255) not NULL,
    Detail TEXT not NULL,

    PRIMARY KEY(ID_zaznamu),

    ID_zvirete INT not NULL,
    FOREIGN KEY(ID_zvirete) REFERENCES Zvire(ID_zvirete) ON DELETE CASCADE,
        -- když se smaže zvíře, potom se smažou i jeho záznamy

    ID_veterinare INT not NULL, -- odkazuje na ID_uzivatele z tabulky Uzivatel (Veterinar)
    FOREIGN KEY(ID_veterinare) REFERENCES Uzivatel(ID_uzivatele)
        -- při smazání veterináře nechceme aby se odstranily i záznamy
);

-- <<week>> entita --
CREATE TABLE Fotka_zvirete (
    ID_fotky INT AUTO_INCREMENT not NULL,
    Cesta_k_obrazku VARCHAR(255) not NULL,

    PRIMARY KEY(ID_fotky),

    ID_zvirete INT not NULL, -- cizí klíč na zvíře
    FOREIGN KEY(ID_zvirete) REFERENCES Zvire(ID_zvirete) ON DELETE CASCADE
        -- odstranění fotek, pokud je zvíře odstraněno
);

CREATE TABLE Uzivatel (
    ID_uzivatele INT AUTO_INCREMENT not NULL,
    Jmeno VARCHAR(255) not NULL,
    Prijmeni VARCHAR(255) not NULL,
    Uzivatelske_jmeno VARCHAR(255) not NULL, -- Username
    Heslo VARCHAR(24) not NULL,
    Email VARCHAR(255) not NULL,
    Telefon VARCHAR(9) not NULL, -- tel. předvolba nebude

    PRIMARY KEY(ID_uzivatele),

    CHECK (REGEXP_LIKE(Uzivatelske_jmeno, '^[a-zA-Z0-9._]{3,}$')),
        -- Username musí mít alespoň 3 znaky
    CHECK (REGEXP_LIKE(Heslo, '^[a-zA-Z0-9@#$%!*_.]{8,}$')),
        -- Heslo má jen některé povolené znaky a musí být alespoň 8 znaků dlouhé
    CHECK (REGEXP_LIKE(Email, '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')),
    CHECK (REGEXP_LIKE(Telefon, '^[0-9]{9}$'))
);

-- (specializace/generalizace -> Uzivatel) --
CREATE TABLE Pecovatel (
    ID_uzivatele INT not NULL,

    PRIMARY KEY(ID_uzivatele),
    FOREIGN KEY(ID_uzivatele) REFERENCES Uzivatel(ID_uzivatele) ON DELETE CASCADE
);

-- (specializace/generalizace -> Uzivatel) --
CREATE TABLE Dobrovolnik (
    ID_uzivatele INT not NULL,
    Overenost BOOLEAN not NULL, -- false = není ověřen, true = je ověřen

    PRIMARY KEY(ID_uzivatele),
    FOREIGN KEY(ID_uzivatele) REFERENCES Uzivatel(ID_uzivatele) ON DELETE CASCADE
);

-- (specializace/generalizace -> Uzivatel) --
CREATE TABLE Administrator (
    ID_uzivatele INT not NULL,

    PRIMARY KEY(ID_uzivatele),
    FOREIGN KEY(ID_uzivatele) REFERENCES Uzivatel(ID_uzivatele) ON DELETE CASCADE
);

-- (specializace/generalizace -> Uzivatel) --
CREATE TABLE Veterinar (
    ID_uzivatele INT not NULL,

    PRIMARY KEY(ID_uzivatele),
    FOREIGN KEY(ID_uzivatele) REFERENCES Uzivatel(ID_uzivatele) ON DELETE CASCADE
);

CREATE TABLE Rezervace (
    ID_rezervace INT AUTO_INCREMENT not NULL,
    Zacatek DATETIME not NULL, -- datum + čas
    Konec DATETIME not NULL, -- datum + čas

    PRIMARY KEY(ID_rezervace),

    ID_zvirete INT not NULL,
    FOREIGN KEY(ID_zvirete) REFERENCES Zvire(ID_zvirete) ON DELETE CASCADE,
     -- odkaz na Zvire, při smazání zvířete se smaže i rezervace

    ID_pecovatele INT not NULL,
    FOREIGN KEY(ID_pecovatele) REFERENCES Uzivatel(ID_uzivatele)
    -- odkaz na Uzivatel, při smazání pečovatele se rezervace zachová
);

-- (specializace/generalizace -> Rezervace) --
CREATE TABLE Venceni (
    ID_rezervace INT not NULL,

    PRIMARY KEY(ID_rezervace),
    FOREIGN KEY(ID_rezervace) REFERENCES Rezervace(ID_rezervace) ON DELETE CASCADE,

    ID_dobrovolnika INT not NULL,
    FOREIGN KEY(ID_dobrovolnika) REFERENCES Uzivatel(ID_uzivatele) ON DELETE CASCADE
        -- při smazání dobrovolníka se smaže i rezervace
);

-- (specializace/generalizace -> Rezervace) --
CREATE TABLE Prohlidka (
    ID_rezervace INT not NULL,

    PRIMARY KEY(ID_rezervace),
    FOREIGN KEY(ID_rezervace) REFERENCES Rezervace(ID_rezervace) ON DELETE CASCADE,

    ID_veterinare INT not NULL,
    FOREIGN KEY(ID_veterinare) REFERENCES Uzivatel(ID_uzivatele) ON DELETE CASCADE
    -- při smazání veterináře se smaže i rezervace
);

-- TODO: naplnit to datama