CREATE TABLE race_cyclists (
    race_id INT REFERENCES races(id),
    cyclist_id INT REFERENCES cyclists(id),
    PRIMARY KEY (race_id, cyclist_id)
);