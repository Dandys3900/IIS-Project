-- MySQL database for IIS project, titled "Animal Shelter"

-- ----------------------------------------------------------------------------------------- --
-- --------------------------------------- DROP TABLE -------------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- It is important to maintain correct order of DROP TABLE (dependencies)

DROP TABLE IF EXISTS Reservation;
DROP TABLE IF EXISTS Task;
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

CREATE TABLE Task (
    taskID INT AUTO_INCREMENT not NULL,
    detail TEXT not NULL,
    isDone BOOLEAN not NULL,

    PRIMARY KEY(taskID),

    animalID INT not NULL,
    FOREIGN KEY(animalID) REFERENCES Animal(animalID) ON DELETE CASCADE,
        -- when the animal is deleted, its tasks are deleted too

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

-- ----------------------------------------------------------------------------------------- --
-- ----------------------------------- INSERT INTO TABLE ----------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- The database will be filled with sample data for easier development

-- ---------------------------------- INSERT INTO ANIMALS ---------------------------------- -

-- Inserting animals
INSERT INTO Animal (species, name, gender, birthDate, arrivalDate, isActive, breed, description)
VALUES
('Pes', 'Max', 0, '2017-04-15', '2022-10-01', TRUE, 'Labrador',
    'Max je přátelský labrador, miluje děti a dlouhé procházky. Váží 32kg.'),
('Pes', 'Bella', 1, '2019-11-20', '2023-01-05', TRUE, 'Labrador',
    'Hrava fenka, vhodná k aktivním majitelům. Váží 26kg.'),
('Pes', 'Rex', 0, '2018-05-10', '2022-09-15', TRUE, 'Německý ovčák',
    'Velký přátelský pes, vhodný pro rodiny s dětmi. Váží 35kg.'),
('Kočka', 'Molly', 1, '2020-07-23', '2023-02-01', TRUE, 'Britská krátkosrstá kočka',
    'Molly je klidná kočka, ráda se mazlí a sleduje okolí. Váží necelé 4kg.'),
('Kočka', 'Jerry', 0, '2019-06-03', '2023-03-05', TRUE, 'Britská krátkosrstá kočka',
    'Jerry je velký kocour, který rád spí. Váží okolo 5kg.'),
('Kočka', 'Kotěnka', 1, NULL, '2023-03-10', TRUE, 'Kočka domácí',
    'Klidná a přítulná kočka, ráda spí v teple. Váží 3kg.'),
('Kočka', 'Simba', 0, '2021-01-30', '2023-04-25', TRUE, 'Siamská kočka',
    'Simba je hravý a energický siamský kocour, rád se honí za hračkami.');

-- Inserting health records for animals
INSERT INTO HealthRecord (name, detail, animalID, veterinarianID)
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

-- -------------------------------- INSERT FOR RESERVATIONS -------------------------------- --

-- -- Inserting reservations for animals
-- INSERT INTO Reservation (start, end, animalID, caregiverID, confirmation)
-- VALUES
-- -- Reservation for Max (Jan Novák - ID 1)
-- ('2023-09-25 10:00:00', '2023-09-25 11:00:00', 1, 1, 'pending'),
-- ('2023-09-26 14:00:00', '2023-09-26 15:00:00', 1, 1, 'pending'),

-- -- Reservation for Bella (Milan Vrbas - ID 2)
-- ('2023-09-25 16:00:00', '2023-09-25 17:00:00', 2, 2, 'pending'),

-- -- Reservation for Rex (Jan Novák - ID 1)
-- ('2023-09-27 09:00:00', '2023-09-27 10:00:00', 3, 1, 'pending'),

-- -- Reservation for Molly (Milan Vrbas - ID 2)
-- ('2023-09-26 09:00:00', '2023-09-26 10:00:00', 4, 2, 'pending'),

-- -- Reservation for Jerry (Jan Novák - ID 1)
-- ('2023-09-28 11:00:00', '2023-09-28 12:00:00', 5, 1, 'pending');

-- -- Inserting walks for animals
-- INSERT INTO Walking (reservationID, volunteerID)
-- VALUES
-- -- Walk for Max (Tomáš Daniel - ID 4)
-- (1, 4),

-- -- Walk for Bella (Eva Králová - ID 6)
-- (3, 6),

-- -- Walk for Rex (Jakub Janšta - ID 5)
-- (4, 5);

-- -- Inserting CheckUps for animals
-- INSERT INTO CheckUp (reservationID, veterinarianID)
-- VALUES
-- -- Checkup for Max (Petr Svoboda - ID 3)
-- (2, 3),

-- -- Checkup for Molly (Petr Svoboda - ID 3)
-- (5, 3);
