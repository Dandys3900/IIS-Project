-- MySQL database for IIS project, titled "Animal Shelter"

-- ----------------------------------------------------------------------------------------- --
-- --------------------------------------- DROP TABLE -------------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- It is important to maintain correct order of DROP TABLE (dependencies)

DROP TABLE IF EXISTS Walking;
DROP TABLE IF EXISTS CheckUp;
DROP TABLE IF EXISTS Reservation;

DROP TABLE IF EXISTS HealthRecord;
DROP TABLE IF EXISTS AnimalPhoto;
DROP TABLE IF EXISTS Animal;

DROP TABLE IF EXISTS Volunteer;
DROP TABLE IF EXISTS Administrator;
DROP TABLE IF EXISTS Veterinarian;
DROP TABLE IF EXISTS Caregiver;

DROP TABLE IF EXISTS Breed;

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
    phoneNumber VARCHAR(9) not NULL, -- phoneNumber prefix not included
    userRole VARCHAR(20) not NULL,

    PRIMARY KEY(userID)
);

-- (specialization/generalization -> User) --
CREATE TABLE Caregiver (
    userID INT not NULL,

    PRIMARY KEY(userID),
    FOREIGN KEY(userID) REFERENCES User(userID) ON DELETE CASCADE
);

-- (specialization/generalization -> User) --
CREATE TABLE Volunteer (
    userID INT not NULL,
    verified BOOLEAN not NULL, -- false = not verified, true = verified

    PRIMARY KEY(userID),
    FOREIGN KEY(userID) REFERENCES User(userID) ON DELETE CASCADE
);

-- (specialization/generalization -> User) --
CREATE TABLE Administrator (
    userID INT not NULL,

    PRIMARY KEY(userID),
    FOREIGN KEY(userID) REFERENCES User(userID) ON DELETE CASCADE
);

-- (specialization/generalization -> User) --
CREATE TABLE Veterinarian (
    userID INT not NULL,

    PRIMARY KEY(userID),
    FOREIGN KEY(userID) REFERENCES User(userID) ON DELETE CASCADE
);

-- ------------------------------------- CREATE ANIMAL ------------------------------------- --

CREATE TABLE Breed (
    breedID INT AUTO_INCREMENT not NULL,
    name VARCHAR(255) not NULL,

    PRIMARY KEY(breedID)
);

CREATE TABLE Animal (
    animalID INT AUTO_INCREMENT not NULL,
    species VARCHAR(255) not NULL,
    name VARCHAR(255) not NULL,
    gender TINYINT not NULL, -- 0 = male, 1 = female
    birthDate DATE, -- can be NULL if the animal's birth date or age is unknown
    arrivalDate DATE not NULL,
    isActive BOOLEAN not NULL, -- false = not in shelter, true = in shelter
    description TEXT not NULL,

    PRIMARY KEY(animalID),

    breedID INT, -- foreign key to Breed table
    FOREIGN KEY(breedID) REFERENCES Breed(breedID) -- Link to Breed
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

-- ---------------------------------- CREATE RESERVATION ----------------------------------- --

CREATE TABLE Reservation (
    reservationID INT AUTO_INCREMENT not NULL,
    start DATETIME not NULL, -- date + time
    end DATETIME not NULL, -- date + time

    PRIMARY KEY(reservationID),

    animalID INT not NULL,
    FOREIGN KEY(animalID) REFERENCES Animal(animalID) ON DELETE CASCADE,
     -- link to Animal, delete reservation if the animal is deleted

    caregiverID INT not NULL,
    FOREIGN KEY(caregiverID) REFERENCES User(userID)
    -- link to User, reservation remains even if the caregiver is deleted
);

-- (specialization/generalization -> Reservation) --
CREATE TABLE Walking (
    reservationID INT not NULL,

    PRIMARY KEY(reservationID),
    FOREIGN KEY(reservationID) REFERENCES Reservation(reservationID) ON DELETE CASCADE,

    volunteerID INT not NULL,
    FOREIGN KEY(volunteerID) REFERENCES User(userID) ON DELETE CASCADE
        -- delete reservation if the volunteer is deleted
);

-- (specialization/generalization -> Reservation) --
CREATE TABLE CheckUp (
    reservationID INT not NULL,

    PRIMARY KEY(reservationID),
    FOREIGN KEY(reservationID) REFERENCES Reservation(reservationID) ON DELETE CASCADE,

    veterinarianID INT not NULL,
    FOREIGN KEY(veterinarianID) REFERENCES User(userID) ON DELETE CASCADE
    -- delete reservation if the veterinarian is deleted
);

-- ----------------------------------------------------------------------------------------- --
-- ----------------------------------- INSERT INTO TABLE ----------------------------------- --
-- ----------------------------------------------------------------------------------------- --

-- The database will be filled with sample data for easier development

-- ---------------------------------- INSERT INTO USER---------------------------------- --

-- Inserting basic users into User table
INSERT INTO User (last_login, firstName, lastName, username, userPassword, email, phoneNumber, userRole)
VALUES
(NULL, 'Jan', 'Novák', 'jnovak', 'Heslo123', 'jan.novak@email.cz', '123456789', 'volunteer'), -- ID 1
(NULL, 'Milan', 'Vrbas', 'Milisaurus', 'C!master7', 'milan.vrbas1@gmail.com', '731672979', 'vet'), -- ID 2
(NULL, 'Petr', 'Svoboda', 'psvoboda', 'Petr*Heslo', 'petr.svoboda@email.com', '987654321', 'carer'), -- ID 3
(NULL, 'Tomáš', 'Daniel', 'xDandys', 'Gym_Monster', 'tomas.daniel@centrum.cz', '731572983', 'admin'), -- ID 4
(NULL, 'Janšta', 'Jakub', 'Kubalabambula', 'Godot#Master', 'jakub.jansta@gmail.com', '732315134', 'admin'), -- ID 5
(NULL, 'Eva', 'Kralová', 'ekralova', 'Kralova@', 'eva.kralova@gmail.com', '555555555', 'volunteer'), -- ID 6
(NULL, 'Marie', 'Novotná', 'mnovotna', 'MarieHeslo420', 'marie.novotna@seznam.cz', '624421413', 'carer'); -- ID 7

-- ---------------------------------- INSERT INTO ANIMALS ---------------------------------- --

-- Inserting breeds
INSERT INTO Breed (name) VALUES
('Labrador'),
('Německý ovčák'),
('Britská krátkosrstá kočka'),
('Kočka domácí'),
('Siamská kočka');

-- Inserting animals
INSERT INTO Animal (species, name, gender, birthDate, arrivalDate, isActive, description, breedID)
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

-- Inserting animal photos (for illustration only)
INSERT INTO AnimalPhoto (imagePath, animalID)
VALUES
-- Photos for Max
('../images/max_1.jpg', 1),
('../images/max_2.jpg', 1),

-- Photos for Bella
('../images/bella_1.jpg', 2),

-- Photos for Rex
('../images/rex_1.jpg', 3),

-- Photos for Molly
('../images/molly_1.jpg', 4),
('../images/molly_2.jpg', 4),

-- Photos for Jerry
('../images/jerry_1.jpg', 5),

-- Photos for Kotěnka
('../images/kittenka_1.jpg', 6),

-- Photos for Simba
('../images/simba_1.jpg', 7);

-- -------------------------------- INSERT FOR RESERVATIONS -------------------------------- --

-- Inserting reservations for animals
INSERT INTO Reservation (start, end, animalID, caregiverID)
VALUES
-- Reservation for Max (Jan Novák - ID 1)
('2023-09-25 10:00:00', '2023-09-25 11:00:00', 1, 1),
('2023-09-26 14:00:00', '2023-09-26 15:00:00', 1, 1),

-- Reservation for Bella (Milan Vrbas - ID 2)
('2023-09-25 16:00:00', '2023-09-25 17:00:00', 2, 2),

-- Reservation for Rex (Jan Novák - ID 1)
('2023-09-27 09:00:00', '2023-09-27 10:00:00', 3, 1),

-- Reservation for Molly (Milan Vrbas - ID 2)
('2023-09-26 09:00:00', '2023-09-26 10:00:00', 4, 2),

-- Reservation for Jerry (Jan Novák - ID 1)
('2023-09-28 11:00:00', '2023-09-28 12:00:00', 5, 1);

-- Inserting walks for animals
INSERT INTO Walking (reservationID, volunteerID)
VALUES
-- Walk for Max (Tomáš Daniel - ID 4)
(1, 4),

-- Walk for Bella (Eva Králová - ID 6)
(3, 6),

-- Walk for Rex (Jakub Janšta - ID 5)
(4, 5);

-- Inserting CheckUps for animals
INSERT INTO CheckUp (reservationID, veterinarianID)
VALUES
-- Checkup for Max (Petr Svoboda - ID 3)
(2, 3),

-- Checkup for Molly (Petr Svoboda - ID 3)
(5, 3);
