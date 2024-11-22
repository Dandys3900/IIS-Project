-- MySQL database for IIS project, titled "Animal Shelter"

-- ----------------------------------------------------------------------------------------- --
-- --------------------------------------- DROP TABLE -------------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- It is important to maintain correct order of DROP TABLE (dependencies)

DROP TABLE IF EXISTS Task;
DROP TABLE IF EXISTS Reservation;
DROP TABLE IF EXISTS HealthRecord;
DROP TABLE IF EXISTS AnimalPhoto;
DROP TABLE IF EXISTS Animal;
DROP TABLE IF EXISTS User;

-- ----------------------------------------------------------------------------------------- --
-- -------------------------------------- CREATE TABLE ------------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- -------------------------------------- CREATE USER -------------------------------------- --
CREATE TABLE User (
    last_login DATETIME(6),
    userID INT AUTO_INCREMENT not NULL,
    firstName VARCHAR(255) not NULL,
    lastName VARCHAR(255) not NULL,
    username VARCHAR(255) not NULL,
    userPassword VARCHAR(24) not NULL,
    email VARCHAR(255) not NULL,
    phoneNumber VARCHAR(13) not NULL, -- in format +420XXXYYYZZZ
    userRole VARCHAR(20) not NULL,
    verified BOOLEAN not NULL, -- relevant only for volunteers

    PRIMARY KEY(userID)
);

-- ------------------------------------- CREATE ANIMAL ------------------------------------- --

CREATE TABLE Animal (
    animalID INT AUTO_INCREMENT not NULL,
    species VARCHAR(255) not NULL,
    name VARCHAR(255) not NULL,
    gender TINYINT not NULL, -- 0 = male, 1 = female
    birthDate DATE, -- can be NULL if the animal's birth date or age is unknown
    arrivalDate DATE not NULL,
    isActive BOOLEAN not NULL, -- false = not in shelter, true = in shelter
    breed VARCHAR(255) not NULL,
    description TEXT not NULL,

    PRIMARY KEY(animalID)
);

-- <<week>> entity --
CREATE TABLE AnimalPhoto (
    photoID INT AUTO_INCREMENT not NULL,
    imagePath VARCHAR(255) not NULL,

    PRIMARY KEY(photoID),
    animalID INT not NULL, -- foreign key to Animal
    FOREIGN KEY(animalID) REFERENCES Animal(animalID) ON DELETE CASCADE
        -- delete photos if the animal is deleted
);

-- ---------------------------------- CREATE HEALTHRECORD ---------------------------------- --

CREATE TABLE HealthRecord (
    recordID INT AUTO_INCREMENT not NULL,
    name VARCHAR(255) not NULL,
    detail TEXT not NULL,

    PRIMARY KEY(recordID),

    animalID INT not NULL,
    FOREIGN KEY(animalID) REFERENCES Animal(animalID) ON DELETE CASCADE,
        -- when the animal is deleted, its health records are deleted too

    veterinarianID INT not NULL, -- references userID from User (Veterinarian)
    FOREIGN KEY(veterinarianID) REFERENCES User(userID)
        -- do not delete records if the veterinarian is deleted
);

-- ---------------------------------- CREATE RESERVATION ----------------------------------- --

CREATE TABLE Reservation (
    reservationID INT AUTO_INCREMENT not NULL,
    PRIMARY KEY(reservationID),

    start DATETIME not NULL, -- date + time
    end DATETIME not NULL, -- date + time

    type VARCHAR(16) not NULL, -- walk/checkup/...

    animalID INT not NULL,
    FOREIGN KEY(animalID) REFERENCES Animal(animalID) ON DELETE CASCADE,
     -- link to Animal, delete reservation if the animal is deleted

    ownerID INT not NULL,
    FOREIGN KEY(ownerID) REFERENCES User(userID),
    -- link to User, reservation remains even if the owner is deleted

    confirmation VARCHAR(9) not NULL -- pending/declined/approved/...
);

-- ------------------------------------- CREATE TASK --------------------------------------- --

CREATE TABLE Task (
    taskID INT AUTO_INCREMENT not NULL,
    detail TEXT not NULL,
    isDone BOOLEAN not NULL,

    PRIMARY KEY(taskID),

    animalID INT not NULL,
    FOREIGN KEY(animalID) REFERENCES Animal(animalID) ON DELETE CASCADE,
        -- when the animal is deleted, its tasks are deleted too

    veterinarianID INT not NULL, -- references userID from User (Veterinarian)
    FOREIGN KEY(veterinarianID) REFERENCES User(userID),
        -- do not delete records if the veterinarian is deleted

    reservationID INT NULL, -- when Task is created, Reservation won't exist (yet)
    FOREIGN KEY(reservationID) REFERENCES Reservation(reservationID) ON DELETE SET NULL
);

-- ----------------------------------------------------------------------------------------- --
-- ----------------------------------- INSERT INTO TABLE ----------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- The database will be filled with sample data for easier development

-- ------------------------------- LIST OF USERS WITH ROLES -------------------------------- --

-- for security reasons, insertion into the user is done in migrations/0005_create_users.py

-- Jan Novák, dobrovolník, ID 1
-- Milan Vrbas, veterinář, ID 2
-- Petr Svoboda, pečovatel, ID 3
-- Tomáš Daniel, administrátor, ID 4
-- Jakub Janšta, administrátor, ID 5
-- Eva Králová, dobrovolník, ID 6
-- Marie Novotná, pečovatel, ID 7

-- ---------------------------------- INSERT INTO ANIMALS ---------------------------------- --

-- Inserting animals
INSERT INTO Animal (species, name, gender, birthDate, arrivalDate, isActive, breed, description)
VALUES
-- Pes Max, ID 1
('Pes', 'Max', 0, '2018-05-10', '2024-03-15', TRUE, 'Labrador',
    'Max je přátelský a energický labrador, který miluje děti a dlouhé procházky přírodou.
    Je velmi chytrý, rád se učí nové triky a přizpůsobí se každému prostředí.
    Váží přibližně 32 kg.'),

-- Pes Bella, ID 2
('Pes', 'Bella', 1, '2020-08-20', '2024-01-10', TRUE, 'Labrador',
    'Bella je hravá a oddaná fenka, která má ráda společnost lidí i jiných psů.
    Ideální volba pro aktivní rodinu, která tráví hodně času venku.
    Váží přibližně 26 kg.'),

-- Pes Rex, ID 3
('Pes', 'Rex', 0, '2019-03-25', '2023-12-01', TRUE, 'Německý ovčák',
    'Rex je velký a přátelský německý ovčák. Je velmi věrný a ochotný chránit svou rodinu.
    Hodí se pro majitele, kteří mu zajistí dostatek pohybu a stimulace. Váží přibližně 35 kg.'),

-- Kočka Molly, ID 4
('Kočka', 'Molly', 1, '2022-01-15', '2024-06-20', TRUE, 'Britská krátkosrstá kočka',
    'Molly je klidná a mazlivá britská krátkosrstá kočka, která ráda pozoruje okolí a užívá
    si klidné chvíle. Váží přibližně 4 kg.'),

-- Kočka Jerry, ID 5
('Kočka', 'Jerry', 0, '2021-05-10', '2024-04-15', TRUE, 'Britská krátkosrstá kočka',
    'Jerry je velký a pohodový kocour, který si užívá klid a spánek. Je to nenáročný
    společník, který ocení klidné prostředí. Váží přibližně 5 kg.'),

-- Kočka Kotěnka, ID 6
('Kočka', 'Kotěnka', 1, '2023-02-10', '2024-03-20', TRUE, 'Kočka domácí',
    'Kotěnka je mladá a přítulná kočka, která si rychle oblíbí každého, kdo ji dá lásku.
    Miluje teplo a ráda tráví čas v blízkosti svého majitele. Váží přibližně 3 kg.'),

-- Kočka Simba, ID 7
('Kočka', 'Simba', 0, '2022-08-15', '2024-05-10', TRUE, 'Siamská kočka',
    'Simba je hravý a zvědavý siamský kocour, který miluje hračky a pozornost.
    Je velmi aktivní a potřebuje podnětné prostředí, aby byl šťastný. Váží přibližně 4,5 kg.'),

-- Králík Lola, ID 8
('Králík', 'Lola', 1, '2023-04-15', '2024-05-20', TRUE, 'Zakrslý beran',
    'Lola je jemná a klidná samička, která si rychle získá vaše srdce. Miluje mazlení a ráda
    tráví dlouhé chvíle okusováním čerstvé zeleniny. Váží přibližně 1,2 kg.'),

-- Králík Charlie, ID 9
('Králík', 'Charlie', 0, '2022-08-10', '2024-06-25', TRUE, 'Zakrslý rex',
    'Charlie je energický a zvědavý králíček, který si užívá skákání a objevování nových
    prostředí. Je velmi hravý, ale potřebuje hodně prostoru na pohyb.
    Skvělý parťák pro aktivní majitele. Váží přibližně 0,9 kg.'),

-- Morče Bublinka, ID 10
('Morče', 'Bublinka', 1, '2023-05-10', '2024-09-01', TRUE, 'Anglické hladkosrsté morče',
    'Bublina je přítulné a zvědavé morče, které si užívá pozornost a ráda si pochutnává na
    čerstvé zelenině, zejména okurce a mrkvi. Je vhodná do domácnosti s dětmi, které ji budou
    věnovat lásku. Váží přibližně 0,8 kg.');


-- ------------------------------- INSERT INTO HEALTHRECORD -------------------------------- --
INSERT INTO HealthRecord (name, detail, animalID, veterinarianID)
VALUES
-- Only one veterinarian - Milan Vrbas ID 2
-- Max (Pes, ID 1)
('Očkování', 'Max byl očkován proti vzteklině a psince.', 1, 2),
('Prohlídka', 'Během kontroly byla zjištěna nadváha, doporučeno více pohybu.', 1, 2),

-- Bella (Pes, ID 2)
('Kastrace', 'Bella byla úspěšně kastrována.', 2, 2),
('Prohlídka', 'Bella má v pořádku srst a váhu.', 2, 2),

-- Rex (Pes, ID 3)
('Očkování', 'Rex byl očkován proti vzteklině.', 3, 2),
('Fyzická terapie', 'Rex zahájil fyzioterapii pro zlepšení pohyblivosti kyčlí.', 3, 2),

-- Molly (Kočka, ID 4)
('Prohlídka', 'Molly má čisté uši a oči, je zdravá.', 4, 2),

-- Jerry (Kočka, ID 5)
('Odčervení', 'Jerry prošel úspěšným odčervením.', 5, 2),
('Problémy s nadváhou', 'Jerry má nadváhu, doporučena redukční dieta.', 5, 2),

-- Kotěnka (Kočka, ID 6)
('Prohlídka', 'Kotěnka je zdravá, ale doporučena prevence proti blechám.', 6, 2),

-- Simba (Kočka, ID 7)
('Očkování', 'Simba byl očkován proti vzteklině.', 7, 2),
('Zranění tlapky', 'Simba měl drobné poranění tlapky, ošetřeno antiseptikem.', 7, 2),

-- Lola (Králík, ID 8)
('Prohlídka', 'Lola má zdravý chrup a srst, doporučeno pokračovat ve správné stravě.', 8, 2),

-- Charlie (Králík, ID 9)
('Očkování', 'Charlie byl očkován proti myxomatóze a moru králíků.', 9, 2),
('Problémy s tlapkami', 'Charlie měl drobný zánět na tlapkách, aplikován antiseptický krém.', 9, 2),

-- Bublinka (Morče, ID 10)
('Prohlídka', 'Bublinka má zdravé zuby a srst, doporučeno pravidelné stříhání drápků.', 10, 2);

-- -------------------------------- INSERT FOR RESERVATIONS -------------------------------- --

-- Inserting reservations for animals
INSERT INTO Reservation (start, end, type, animalID, ownerID, confirmation)
VALUES
-- -------------------------------- Old checkup reservations ------------------------------- --
-- Max (Pes, ID 1)
('2024-11-01 09:00:00', '2024-11-01 09:30:00', 'checkup', 1, 2, 'approved'), -- Reservation ID 1
('2024-11-02 10:00:00', '2024-11-02 10:30:00', 'checkup', 1, 2, 'approved'), -- Reservation ID 2

-- Bella (Pes, ID 2)
('2024-10-01 11:00:00', '2024-10-01 11:30:00', 'checkup', 2, 2, 'approved'), -- Reservation ID 3
('2024-10-03 14:00:00', '2024-10-03 14:30:00', 'checkup', 2, 2, 'approved'), -- Reservation ID 4

-- Rex (Pes, ID 3)
('2024-09-10 09:00:00', '2024-09-10 09:30:00', 'checkup', 3, 2, 'approved'), -- Reservation ID 5
('2024-09-15 10:00:00', '2024-09-15 10:30:00', 'checkup', 3, 2, 'approved'), -- Reservation ID 6

-- Molly (Kočka, ID 4)
('2024-08-05 10:00:00', '2024-08-05 10:30:00', 'checkup', 4, 2, 'approved'), -- Reservation ID 7

-- Jerry (Kočka, ID 5)
('2024-07-01 11:00:00', '2024-07-01 11:30:00', 'checkup', 5, 2, 'approved'), -- Reservation ID 8
('2024-07-05 15:00:00', '2024-07-05 15:30:00', 'checkup', 5, 2, 'approved'), -- Reservation ID 9

-- Kotěnka (Kočka, ID 6)
('2024-06-10 10:00:00', '2024-06-10 10:30:00', 'checkup', 6, 2, 'approved'), -- Reservation ID 10

-- Simba (Kočka, ID 7)
('2024-05-15 09:00:00', '2024-05-15 09:30:00', 'checkup', 7, 2, 'approved'), -- Reservation ID 11
('2024-05-20 14:00:00', '2024-05-20 14:30:00', 'checkup', 7, 2, 'approved'), -- Reservation ID 12

-- Lola (Králík, ID 8)
('2024-04-01 11:00:00', '2024-04-01 11:30:00', 'checkup', 8, 2, 'approved'), -- Reservation ID 13

-- Charlie (Králík, ID 9)
('2024-03-10 09:00:00', '2024-03-10 09:30:00', 'checkup', 9, 2, 'approved'), -- Reservation ID 14
('2024-03-15 10:00:00', '2024-03-15 10:30:00', 'checkup', 9, 2, 'approved'), -- Reservation ID 15

-- Bublinka (Morče, ID 10)
('2024-08-06 15:00:00', '2024-08-06 16:00:00', 'checkup', 10, 2, 'approved'), -- Reservation ID 16

-- ----------------------------- Future checkup reservations ------------------------------- --
-- Max (Pes, ID 1)
('2024-12-20 09:00:00', '2024-12-20 09:30:00', 'checkup', 1, 2, 'pending'), -- Reservation ID 17
('2024-12-22 10:00:00', '2024-12-22 10:30:00', 'checkup', 1, 2, 'pending'), -- Reservation ID 18

-- Bella (Pes, ID 2)
('2024-12-24 11:00:00', '2024-12-24 11:30:00', 'checkup', 2, 2, 'approved'), -- Reservation ID 19

-- Simba (Kočka, ID 7)
('2024-12-27 14:00:00', '2024-12-27 14:30:00', 'checkup', 7, 2, 'approved'), -- Reservation ID 20

-- Bublinka (Morče, ID 10)
('2024-12-30 15:00:00', '2024-12-30 15:30:00', 'checkup', 10, 2, 'approved'), -- Reservation ID 21

-- -------------------------------- Old walk reservations ---------------------------------- --
-- Max (Pes, ID 1)
('2024-06-01 09:00:00', '2024-06-04 19:00:00', 'walk', 1, 1, 'approved'), -- Reservation ID 22
('2024-07-10 10:00:00', '2024-07-13 18:00:00', 'walk', 1, 1, 'approved'), -- Reservation ID 23

-- Bella (Pes, ID 2)
('2024-05-01 10:00:00', '2024-05-04 18:00:00', 'walk', 2, 6, 'approved'), -- Reservation ID 24
('2024-06-20 09:00:00', '2024-06-23 19:00:00', 'walk', 2, 6, 'approved'), -- Reservation ID 25
('2024-07-15 10:00:00', '2024-07-18 20:00:00', 'walk', 2, 6, 'declined'), -- Reservation ID 26

-- Rex (Pes, ID 3)
('2024-04-01 10:00:00', '2024-04-04 18:00:00', 'walk', 3, 1, 'approved'), -- Reservation ID 27
('2024-05-15 09:00:00', '2024-05-18 20:00:00', 'walk', 3, 1, 'approved'), -- Reservation ID 28

-- Jerry (Kočka, ID 5)
('2024-04-05 10:00:00', '2024-04-08 18:00:00', 'walk', 5, 6, 'approved'), -- Reservation ID 29
('2024-05-25 09:00:00', '2024-05-28 20:00:00', 'walk', 5, 6, 'approved'), -- Reservation ID 30

-- Simba (Kočka, ID 7)
('2024-03-20 09:00:00', '2024-03-23 19:00:00', 'walk', 7, 6, 'approved'), -- Reservation ID 31
('2024-04-15 10:00:00', '2024-04-18 18:00:00', 'walk', 7, 6, 'declined'), -- Reservation ID 32
('2024-05-05 09:00:00', '2024-05-08 20:00:00', 'walk', 7, 6, 'approved'), -- Reservation ID 33

-- Lola (Králík, ID 8)
('2024-02-01 10:00:00', '2024-02-04 19:00:00', 'walk', 8, 1, 'approved'), -- Reservation ID 34
('2024-03-10 09:00:00', '2024-03-13 18:00:00', 'walk', 8, 1, 'approved'), -- Reservation ID 35

-- Charlie (Králík, ID 9)
('2024-01-15 10:00:00', '2024-01-18 18:00:00', 'walk', 9, 6, 'declined'), -- Reservation ID 36
('2024-02-10 09:00:00', '2024-02-13 19:00:00', 'walk', 9, 6, 'approved'), -- Reservation ID 37
('2024-03-05 10:00:00', '2024-03-08 20:00:00', 'walk', 9, 6, 'approved'), -- Reservation ID 38

-- Bublinka (Morče, ID 10)
('2024-01-10 09:00:00', '2024-01-13 18:00:00', 'walk', 10, 6, 'approved'), -- Reservation ID 39
('2024-02-05 10:00:00', '2024-02-08 19:00:00', 'walk', 10, 1, 'approved'), -- Reservation ID 40
('2024-03-15 09:00:00', '2024-03-18 20:00:00', 'walk', 10, 6, 'declined'), -- Reservation ID 41

-- ------------------------------- Future walk reservations -------------------------------- --
-- Max (Pes, ID 1)
('2024-12-20 09:00:00', '2024-12-23 18:00:00', 'walk', 1, 6, 'pending'), -- Reservation ID 42
('2025-01-10 10:00:00', '2025-01-13 17:00:00', 'walk', 1, 1, 'approved'), -- Reservation ID 43

-- Bella (Pes, ID 2)
('2024-11-25 10:00:00', '2024-11-28 19:00:00', 'walk', 2, 1, 'approved'), -- Reservation ID 44
('2025-02-01 11:00:00', '2025-02-04 20:00:00', 'walk', 2, 6, 'pending'), -- Reservation ID 45

-- Rex (Pes, ID 3)
('2024-12-05 09:00:00', '2024-12-08 18:00:00', 'walk', 3, 6, 'approved'), -- Reservation ID 46
('2025-03-15 12:00:00', '2025-03-18 18:30:00', 'walk', 3, 1, 'declined'), -- Reservation ID 47

-- Molly (Kočka, ID 4)
('2024-11-30 08:00:00', '2024-12-03 16:30:00', 'walk', 4, 1, 'approved'), -- Reservation ID 48
('2025-01-15 09:30:00', '2025-01-18 19:00:00', 'walk', 4, 6, 'pending'), -- Reservation ID 49

-- Jerry (Kočka, ID 5)
('2024-12-25 10:00:00', '2024-12-28 19:00:00', 'walk', 5, 6, 'approved'), -- Reservation ID 50
('2025-02-20 09:00:00', '2025-02-23 17:30:00', 'walk', 5, 1, 'pending'), -- Reservation ID 51

-- Kotěnka (Kočka, ID 6)
('2024-11-20 10:30:00', '2024-11-23 18:00:00', 'walk', 6, 6, 'approved'), -- Reservation ID 52
('2025-03-01 11:00:00', '2025-03-04 20:00:00', 'walk', 6, 1, 'pending'), -- Reservation ID 53

-- Simba (Kočka, ID 7)
('2024-12-10 09:00:00', '2024-12-13 18:30:00', 'walk', 7, 1, 'approved'), -- Reservation ID 54
('2025-01-20 10:00:00', '2025-01-23 19:00:00', 'walk', 7, 6, 'approved'), -- Reservation ID 55

-- Lola (Králík, ID 8)
('2024-11-15 09:00:00', '2024-11-18 18:00:00', 'walk', 8, 1, 'pending'), -- Reservation ID 56
('2025-02-10 10:00:00', '2025-02-13 17:30:00', 'walk', 8, 6, 'approved'), -- Reservation ID 57

-- Charlie (Králík, ID 9)
('2024-11-18 09:00:00', '2024-11-21 18:00:00', 'walk', 9, 1, 'approved'), -- Reservation ID 58
('2025-03-05 10:30:00', '2025-03-08 18:30:00', 'walk', 9, 6, 'pending'), -- Reservation ID 59

-- Bublinka (Morče, ID 10)
('2024-12-01 10:00:00', '2024-12-04 19:00:00', 'walk', 10, 1, 'approved'), -- Reservation ID 60
('2025-01-25 09:30:00', '2025-01-28 17:30:00', 'walk', 10, 6, 'approved'); -- Reservation ID 61


-- Future Reservation for Lola (Králík, ID 8) - ('Prohlídka blech', FALSE, 8, 2, 62) not yet created

-- ----------------------------------- INSERT INTO TASK ------------------------------------ --

INSERT INTO Task (detail, isDone, animalID, veterinarianID, reservationID)
VALUES
-- ---------------------------------- Accomplished tasks ----------------------------------- --
-- Max (Pes, ID 1)
('Očkování proti vzteklině a psince', TRUE, 1, 2, 1),
('Kontrola kvůli nadváze', TRUE, 1, 2, 2),

-- Bella (Pes, ID 2)
('Kastrace', TRUE, 2, 2, 3),
('Běžná prohlídka srsti a váhy', TRUE, 2, 2, 4),

-- Rex (Pes, ID 3)
('Očkování proti vzteklině', TRUE, 3, 2, 5),
('Fyzioterapie pro zlepšení pohyblivosti kyčlí', TRUE, 3, 2, 6),

-- Molly (Kočka, ID 4)
('Běžná kontrola zdravotního stavu', TRUE, 4, 2, 7),

-- Jerry (Kočka, ID 5)
('Odčervení', TRUE, 5, 2, 8),
('Kontrola kvůli nadváze', TRUE, 5, 2, 9),

-- Kotěnka (Kočka, ID 6)
('Prevence proti blechám', TRUE, 6, 2, 10),

-- Simba (Kočka, ID 7)
('Očkování proti vzteklině', TRUE, 7, 2, 11),
('Ošetření drobného poranění tlapky', TRUE, 7, 2, 12),

-- Lola (Králík, ID 8)
('Běžná kontrola chrupu a srsti', TRUE, 8, 2, 13),

-- Charlie (Králík, ID 9)
('Očkování proti myxomatóze a moru králíků', TRUE, 9, 2, 14),
('Ošetření drobného zánětu tlapek', TRUE, 9, 2, 15),

-- Bublinka (Morče, ID 10)
('Běžná kontrola zdravotního stavu', TRUE, 10, 2, 16),

-- ------------------------------------- Future tasks -------------------------------------- --
-- Max (Pes, ID 1)
('Prohlídka zubů a uší', FALSE, 1, 2, 17),
('Očkování proti klíšťatům', FALSE, 1, 2, 18),

-- Bella (Pes, ID 2)
('Vyšetření pohyblivosti', FALSE, 2, 2, 19),

-- Simba (Kočka, ID 7)
('Kontrola stavu srsti', FALSE, 7, 2, 20),

-- Bublinka (Morče, ID 10)
('Kontrola váhy a doporučení stravy', FALSE, 10, 2, 21),

-- Lola (Králík, ID 8)
('Prohlídka blech', FALSE, 8, 2, NULL); -- reservation does not exist
