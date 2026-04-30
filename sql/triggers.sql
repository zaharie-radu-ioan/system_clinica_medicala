DROP TRIGGER IF EXISTS trg_programari_before_insert;
--TRIGGER_END

CREATE TRIGGER trg_programari_before_insert
BEFORE INSERT ON programare
FOR EACH ROW
BEGIN
    IF NEW.data < CURRENT_DATE THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Eroare: Nu poti crea o programare in trecut.';
    END IF;
END;
--TRIGGER_END

DROP TRIGGER IF EXISTS trg_programari_after_update;
--TRIGGER_END

CREATE TRIGGER trg_programari_after_update
AFTER UPDATE ON programare
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO user_log (id_utilizator, actiune)
        VALUES (
            1,
            CONCAT('Status programare ', NEW.id_programare, ' schimbat din ', OLD.status, ' in ', NEW.status)
        );
    END IF;
END;
--TRIGGER_END

DROP TRIGGER IF EXISTS trg_programari_after_insert;
--TRIGGER_END

CREATE TRIGGER trg_programari_after_insert
AFTER INSERT ON consultatie
FOR EACH ROW
BEGIN
    UPDATE programare SET status='finalizata'
    WHERE id_programare=NEW.id_programare;
END;
--TRIGGER_END
