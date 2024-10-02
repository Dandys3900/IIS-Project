-- MySQL databáze pro IIS projekt, jehož zadáním je "Zvířecí útulek"

-- pozn.    VARCHAR2 a NVARCHAR/NVARCHAR2 ve v MySQL nepoužívají
--          používám VARCHAR(255) - VARCHAR může mít proměnlivou délku

-- ----------------------------------------------------------------------------------------- --
-- --------------------------------------- DROP TABLE -------------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- Důležité je zachování správného pořadí DROP TABLE (dependency)

DROP TABLE IF EXISTS Venceni;
DROP TABLE IF EXISTS Prohlidka;
DROP TABLE IF EXISTS Rezervace;

DROP TABLE IF EXISTS Zdravotni_zaznam;
DROP TABLE IF EXISTS Fotka_zvirete;
DROP TABLE IF EXISTS Zvire;

DROP TABLE IF EXISTS Dobrovolnik;
DROP TABLE IF EXISTS Administrator;
DROP TABLE IF EXISTS Veterinar;
DROP TABLE IF EXISTS Pecovatel;
DROP TABLE IF EXISTS Uzivatel;

DROP TABLE IF EXISTS Plemeno;

-- ----------------------------------------------------------------------------------------- --
-- -------------------------------------- CREATE TABLE ------------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- ---------------------------------- VYTVOŘENÍ UŽIVATELE ---------------------------------- --
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

-- ----------------------------------- VYTVOŘENÍ ZVÍŘETE ----------------------------------- --

CREATE TABLE Plemeno (
    ID_plemene INT AUTO_INCREMENT not NULL,
    Nazev VARCHAR(255) not NULL,

    PRIMARY KEY(ID_plemene)
);

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

-- <<week>> entita --
CREATE TABLE Fotka_zvirete (
    ID_fotky INT AUTO_INCREMENT not NULL,
    Cesta_k_obrazku VARCHAR(255) not NULL,

    PRIMARY KEY(ID_fotky),

    ID_zvirete INT not NULL, -- cizí klíč na zvíře
    FOREIGN KEY(ID_zvirete) REFERENCES Zvire(ID_zvirete) ON DELETE CASCADE
        -- odstranění fotek, pokud je zvíře odstraněno
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

-- ---------------------------------- VYTVOŘENÍ REZERVACE ---------------------------------- --

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

-- ----------------------------------------------------------------------------------------- --
-- ----------------------------------- INSERT INTO TABLE ----------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- Databáze se naplní ukázkovými daty, slouží pro usnadnění vývoje (snad)

-- ---------------------------------- INSERT PRO UŽIVATELE---------------------------------- --

-- Vložení základních uživatelů do tabulky Uzivatel
INSERT INTO Uzivatel (Jmeno, Prijmeni, Uzivatelske_jmeno, Heslo, Email, Telefon)
VALUES 
('Jan', 'Novák', 'jnovak', 'Heslo123', 'jan.novak@email.cz', '123456789'), -- ID 1
('Milan', 'Vrbas', 'Milisaurus', 'C!master7', 'milan.vrbas1@gmail.com', '731672979'), -- ID 2
('Petr', 'Svoboda', 'psvoboda', 'Petr*Heslo', 'petr.svoboda@email.com', '987654321'), -- ID 3
('Tomáš', 'Daniel', 'xDandys', 'Gym_Monster', 'tomas.daniel@centrum.cz', '731572983'), -- ID 4
('Janšta', 'Jakub', 'Kubalabambula', 'Godot#Master', 'jakub.jansta@gmail.com', '732315134'), -- ID 5
('Eva', 'Kralová', 'ekralova', 'Kralova@', 'eva.kralova@gmail.com', '555555555'), -- ID 6
('Marie', 'Novotná', 'mnovotna', 'MarieHeslo420', 'marie.novotna@seznam.cz', '624421413'); -- ID 7

-- Vložení specifických uživatelů (specializace)
INSERT INTO Pecovatel (ID_uzivatele) VALUES (1);  -- Jan Novák
INSERT INTO Pecovatel (ID_uzivatele) VALUES (2);  -- Milan Vrbas
INSERT INTO Veterinar (ID_uzivatele) VALUES (3);  -- Petr Svoboda
INSERT INTO Dobrovolnik (ID_uzivatele, Overenost) VALUES (4, TRUE); -- Tomáš Daniel
INSERT INTO Dobrovolnik (ID_uzivatele, Overenost) VALUES (5, FALSE); -- Jakub Janšta
INSERT INTO Dobrovolnik (ID_uzivatele, Overenost) VALUES (6, FALSE); -- Eva Králová
INSERT INTO Administrator (ID_uzivatele) VALUES (7); -- Marie Novotná

-- ---------------------------------- INSERT PRO ZVÍŘÁTKA ---------------------------------- --

-- Vložení plemen
INSERT INTO Plemeno (Nazev) VALUES 
('Labrador'),
('Německý ovčák'),
('Britská krátkosrstá kočka'),
('Kočka domácí'),
('Siamská kočka');

-- Vložení zvířat
INSERT INTO Zvire (Druh, Jmeno, Pohlavi, Datum_narozeni, Datum_prichodu, Aktivni, Popis, ID_plemene)
VALUES 
('Pes', 'Max', 0, '2017-04-15', '2022-10-01', TRUE, 
    'Max je přátelský labrador, miluje děti a dlouhé procházky. Váží 32kg.', 1), -- Labrador
('Pes', 'Bella', 1, '2019-11-20', '2023-01-05', TRUE, 
    'Hrava fenka, vhodná k aktivním majitelům. Váží 26kg.', 1), -- Labrador
('Pes', 'Rex', 0, '2018-05-10', '2022-09-15', TRUE, 
    'Velký přátelský pes, vhodný pro rodiny s dětmi. Váží 35kg.', 2), -- Německý ovčák
('Kočka', 'Molly', 1, '2020-07-23', '2023-02-01', TRUE, 
    'Molly je klidná kočka, ráda se mazlí a sleduje okolí. Váží necelé 4kg.', 3), -- Britská krátkosrstá kočka
('Kočka', 'Jerry', 0, '2019-06-03', '2023-03-05', TRUE, 
    'Jerry je velký kocour, který rád spí. Váží okolo 5kg.', 3), -- Britská krátkosrstá kočka
('Kočka', 'Kotěnka', 1, NULL, '2023-03-10', TRUE, 
    'Klidná a přítulná kočka, ráda spí v teple. Váží 3kg.', 4), -- Kočka domácí
('Kočka', 'Simba', 0, '2021-01-30', '2023-04-25', TRUE, 
    'Simba je hravý a energický siamský kocour, rád se honí za hračkami.', 5);-- Siamská kočka

-- Vložení zdravotních záznamů pro zvířata
INSERT INTO Zdravotni_zaznam (Nazev, Detail, ID_zvirete, ID_veterinare)
VALUES 
-- Max
('Očkování', 'Max byl očkován proti vzteklině a psince.', 1, 3),
('Prohlídka', 'Během kontroly byla zjištěna nadváha, doporučeno více pohybu.', 1, 3),

-- Bella
('Kastrace', 'Bella byla úspěšně kastrována.', 2, 3),
('Prohlídka', 'Bella má v pořádku srst a váhu.', 2, 3),

-- Rex
('Očkování', 'Rex byl očkován proti vzteklině.', 3, 3),
('Problémy s kyčlemi', 'Diagnostikována dysplazie kyčelního kloubu, doporučena léčba.', 3, 3),

-- Molly
('Prohlídka', 'Molly má čisté uši a oči, je zdravá.', 4, 3),

-- Jerry
('Odčervení', 'Jerry prošel úspěšným odčervením.', 5, 3),

-- Kotěnka
('Prohlídka', 'Kotěnka je zdravá, ale doporučena prevence proti blechám.', 6, 3),

-- Simba
('Očkování', 'Simba byl očkován proti vzteklině.', 7, 3);

-- Vložení fotek zvířat (pouze pro ilustraci)
INSERT INTO Fotka_zvirete (Cesta_k_obrazku, ID_zvirete)
VALUES 
-- Fotky pro Maxe
('../images/max_1.jpg', 1),
('../images/max_2.jpg', 1),

-- Fotky pro Bellu
('../images/bella_1.jpg', 2),

-- Fotky pro Rexe
('../images/rex_1.jpg', 3),

-- Fotky pro Molly
('../images/molly_1.jpg', 4),
('../images/molly_2.jpg', 4),

-- Fotky pro Jerryho
('../images/jerry_1.jpg', 5),

-- Fotky pro Kotěnku
('../images/kotenka_1.jpg', 6),

-- Fotky pro Simbu
('../images/simba_1.jpg', 7);

-- ---------------------------------- INSERT PRO REZERVACE---------------------------------- --

-- Vložení rezervací pro zvířata
INSERT INTO Rezervace (Zacatek, Konec, ID_zvirete, ID_pecovatele)
VALUES
-- Rezervace pro Maxe (Jan Novák - ID 1)
('2023-09-25 10:00:00', '2023-09-25 11:00:00', 1, 1),
('2023-09-26 14:00:00', '2023-09-26 15:00:00', 1, 1),

-- Rezervace pro Bellu (Milan Vrbas - ID 2)
('2023-09-25 16:00:00', '2023-09-25 17:00:00', 2, 2),

-- Rezervace pro Rexe (Jan Novák - ID 1)
('2023-09-27 09:00:00', '2023-09-27 10:00:00', 3, 1),

-- Rezervace pro Molly (Milan Vrbas - ID 2)
('2023-09-26 09:00:00', '2023-09-26 10:00:00', 4, 2),

-- Rezervace pro Jerryho (Jan Novák - ID 1)
('2023-09-28 11:00:00', '2023-09-28 12:00:00', 5, 1);

-- Vložení venčení pro zvířata
INSERT INTO Venceni (ID_rezervace, ID_dobrovolnika)
VALUES
-- Venčení pro Maxe (Tomáš Daniel - ID 4)
(1, 4),

-- Venčení pro Bellu (Eva Králová - ID 6)
(3, 6),

-- Venčení pro Rexe (Jakub Janšta - ID 5)
(4, 5);

-- Vložení prohlídek pro zvířata
INSERT INTO Prohlidka (ID_rezervace, ID_veterinare)
VALUES
-- Prohlídka pro Maxe (Petr Svoboda - ID 3)
(2, 3),

-- Prohlídka pro Molly (Petr Svoboda - ID 3)
(5, 3);