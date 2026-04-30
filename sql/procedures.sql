DROP PROCEDURE IF EXISTS finalizare_consultatie;
-- PROC_END

CREATE PROCEDURE finalizare_consultatie(
    IN p_id_programare INT,
    IN p_diagnostic VARCHAR(255),
    IN p_analize_recomandate TEXT,
    IN p_recomandari_tratament TEXT,
    IN p_servicii_json JSON
)
BEGIN
    DECLARE v_id_consultatie INT;
    DECLARE v_i INT DEFAULT 0;
    DECLARE v_len INT DEFAULT 0;

    DECLARE v_cod_serviciu VARCHAR(50);
    DECLARE v_cantitate INT;

    DECLARE v_id_serviciu INT;
    DECLARE v_pret_unitar DECIMAL(10,2);
    DECLARE v_total_cost DECIMAL(10,2) DEFAULT 0.00;

    INSERT INTO consultatie (id_programare, diagnostic, analize_recomandate, recomandari_tratament)
    VALUES (p_id_programare, p_diagnostic, p_analize_recomandate, p_recomandari_tratament);

    SET v_id_consultatie = LAST_INSERT_ID();
    SET v_len = JSON_LENGTH(p_servicii_json);

    WHILE v_i < v_len DO

        SET v_cod_serviciu = JSON_UNQUOTE(JSON_EXTRACT(p_servicii_json, CONCAT('$[', v_i, '].cod')));
        SET v_cantitate = JSON_EXTRACT(p_servicii_json, CONCAT('$[', v_i, '].qty'));


        SELECT id_serviciu, pret INTO v_id_serviciu, v_pret_unitar
        FROM servicii_medicale
        WHERE cod_serviciu = v_cod_serviciu LIMIT 1;

        -- Inseram in entitatea dependenta (Tabela factura)
        INSERT INTO factura (id_consultatie, id_serviciu, cantitate, pret_unitar)
        VALUES (v_id_consultatie, v_id_serviciu, v_cantitate, v_pret_unitar);

        -- Calculam totalul cumulat pentru header
        SET v_total_cost = v_total_cost + (v_pret_unitar * v_cantitate);

        -- Incrementam indexul buclei
        SET v_i = v_i + 1;
    END WHILE;

    -- 4. Actualizam costul total al consultatiei
    UPDATE consultatie SET cost = v_total_cost WHERE id_consultatie = v_id_consultatie;

    -- Nu mai facem UPDATE pe programare pentru status = 'finalizata'
    -- deoarece trigger-ul `trg_consultatie_after_insert` se ocupa deja de asta!

    -- Returnam ID-ul consultatiei create pentru Python
    SELECT v_id_consultatie AS id_consultatie;
END;
-- PROC_END


DROP PROCEDURE IF EXISTS gestionare_programare;
-- PROC_END

CREATE PROCEDURE gestionare_programare(
    IN p_actiune VARCHAR(20),
    IN p_id_programare INT,
    IN p_data DATE,
    IN p_ora TIME,
    IN p_cabinet VARCHAR(50),
    IN p_id_pacient INT,
    IN p_id_medic INT
)
BEGIN
    IF p_actiune = 'creare' THEN
        -- Adaugam o noua programare
        INSERT INTO programare (data, ora, cabinet, id_pacient, id_medic)
        VALUES (p_data, p_ora, p_cabinet, p_id_pacient, p_id_medic);

        SELECT LAST_INSERT_ID() AS id_programare;

    ELSEIF p_actiune = 'anulare' THEN
        -- Schimbam doar statusul
        UPDATE programare SET status = 'anulata' WHERE id_programare = p_id_programare;

        SELECT p_id_programare AS id_programare;

    ELSEIF p_actiune = 'reprogramare' THEN
        -- Actualizam data si ora programarii existente
        UPDATE programare
        SET data = p_data, ora = p_ora
        WHERE id_programare = p_id_programare;

        SELECT p_id_programare AS id_programare;

    END IF;
END;
-- PROC_END