
-- 1. Tabela master pentru utilizatori
CREATE TABLE IF NOT EXISTS utilizator (
    id_utilizator INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    parola        VARCHAR(255) NOT NULL,
    email         VARCHAR(100) UNIQUE,
    rol           ENUM('admin', 'medic', 'pacient') NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela pentru medici
CREATE TABLE IF NOT EXISTS medic (
    id_medic      INT AUTO_INCREMENT PRIMARY KEY,
    id_utilizator INT          UNIQUE NOT NULL,
    nume_medic    VARCHAR(50)  NOT NULL,
    cod_parafa    INT          NOT NULL UNIQUE,
    specializare  VARCHAR(50)  NOT NULL,
    program       VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_utilizator) REFERENCES utilizator(id_utilizator) ON DELETE CASCADE
);

-- 3. Tabela pentru pacienti
CREATE TABLE IF NOT EXISTS pacient (
    id_pacient    INT AUTO_INCREMENT PRIMARY KEY,
    id_utilizator INT UNIQUE NOT NULL,
    nume          VARCHAR(50) NOT NULL,
    prenume       VARCHAR(50) NOT NULL,
    CNP           VARCHAR(13) NOT NULL UNIQUE,
    data_nasterii DATE        NOT NULL,
    sex           VARCHAR(10) NOT NULL,
    telefon       VARCHAR(15) NOT NULL,
    FOREIGN KEY (id_utilizator) REFERENCES utilizator(id_utilizator) ON DELETE CASCADE
);

-- 4. Dosar medical pacient (date medicale separate de datele de identitate)
CREATE TABLE IF NOT EXISTS dosar_medical (
    id_dosar       INT AUTO_INCREMENT PRIMARY KEY,
    id_pacient     INT NOT NULL UNIQUE,
    grupa_sanguina ENUM('A1', 'A2', 'B', 'AB', 'O'),
    rh             ENUM('+', '-'),
    alergii        TEXT,
    boli_cronice   TEXT,
    observatii     TEXT,
    FOREIGN KEY (id_pacient) REFERENCES pacient(id_pacient) ON DELETE CASCADE
);

-- 5. Tabela pentru programari
CREATE TABLE IF NOT EXISTS programare (
    id_programare INT AUTO_INCREMENT PRIMARY KEY,
    data          DATE        NOT NULL,
    ora           TIME        NOT NULL,
    cabinet       VARCHAR(50) NOT NULL,
    id_pacient    INT         NOT NULL,
    id_medic      INT         NOT NULL,
    id_utilizator INT,
    status        ENUM('programata', 'finalizata', 'anulata') DEFAULT 'programata',
    FOREIGN KEY (id_pacient)    REFERENCES pacient(id_pacient)       ON DELETE CASCADE,
    FOREIGN KEY (id_medic)      REFERENCES medic(id_medic)           ON DELETE CASCADE,
    FOREIGN KEY (id_utilizator) REFERENCES utilizator(id_utilizator) ON DELETE SET NULL
);

-- 6. Tabela de audit / loguri (se va popula automat prin triggere)
CREATE TABLE IF NOT EXISTS user_log (
    id_log        INT AUTO_INCREMENT PRIMARY KEY,
    id_utilizator INT          NOT NULL,
    actiune       VARCHAR(255) NOT NULL,
    ip_address    VARCHAR(45),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilizator) REFERENCES utilizator(id_utilizator) ON DELETE CASCADE
);

-- 7. Tabela principala pentru consultatii (Header factura)
CREATE TABLE IF NOT EXISTS consultatie (
    id_consultatie        INT AUTO_INCREMENT PRIMARY KEY,
    id_programare         INT           NOT NULL UNIQUE,
    diagnostic            VARCHAR(255)  NOT NULL,
    analize_recomandate   TEXT,
    recomandari_tratament TEXT,
    cost                  DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_programare) REFERENCES programare(id_programare) ON DELETE CASCADE
);

-- 8. Catalogul de servicii medicale predefinite
CREATE TABLE IF NOT EXISTS servicii_medicale (
    id_serviciu  INT AUTO_INCREMENT PRIMARY KEY,
    cod_serviciu VARCHAR(50)   UNIQUE NOT NULL,
    denumire     VARCHAR(100)  NOT NULL,
    pret         DECIMAL(10,2) NOT NULL
);

-- 9. Tabela dependenta pentru detaliile facturii (Linii factura)
CREATE TABLE IF NOT EXISTS factura (
    id_linie       INT AUTO_INCREMENT PRIMARY KEY,
    id_consultatie INT           NOT NULL,
    id_serviciu    INT           NOT NULL,
    cantitate      INT           NOT NULL DEFAULT 1,
    pret_unitar    DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_consultatie) REFERENCES consultatie(id_consultatie) ON DELETE CASCADE,
    FOREIGN KEY (id_serviciu)    REFERENCES servicii_medicale(id_serviciu)
);

-- 10. Catalog medicamente
CREATE TABLE IF NOT EXISTS medicament (
    id_medicament INT AUTO_INCREMENT PRIMARY KEY,
    denumire      VARCHAR(100) NOT NULL UNIQUE,
    prospect      TEXT,
    forma         VARCHAR(50)       -- 'comprimate', 'sirop', 'injectabil', etc.
);

-- 11. Retete emise la o consultatie
CREATE TABLE IF NOT EXISTS reteta (
    id_reteta      INT AUTO_INCREMENT PRIMARY KEY,
    id_consultatie INT  NOT NULL,
    data_emiterii  DATE NOT NULL,
    valabila_pana  DATE,
    FOREIGN KEY (id_consultatie) REFERENCES consultatie(id_consultatie) ON DELETE CASCADE
);

-- 12. Linii reteta - relatie M:N intre reteta si medicament (cu atribute pe relatie)
CREATE TABLE IF NOT EXISTS reteta_medicament (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    id_reteta     INT          NOT NULL,
    id_medicament INT          NOT NULL,
    doza          VARCHAR(100),       -- ex: '500mg'
    frecventa     VARCHAR(100),       -- ex: 'de 3 ori pe zi'
    durata        VARCHAR(50),        -- ex: '7 zile'
    FOREIGN KEY (id_reteta)     REFERENCES reteta(id_reteta)         ON DELETE CASCADE,
    FOREIGN KEY (id_medicament) REFERENCES medicament(id_medicament)
);

-- 13. Notificari catre utilizatori
CREATE TABLE IF NOT EXISTS notificare (
    id_notificare INT AUTO_INCREMENT PRIMARY KEY,
    id_utilizator INT          NOT NULL,
    mesaj         VARCHAR(255) NOT NULL,
    tip           ENUM('reminder', 'anulare', 'confirmare', 'sistem') NOT NULL,
    citita        BOOLEAN   DEFAULT FALSE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilizator) REFERENCES utilizator(id_utilizator) ON DELETE CASCADE
);