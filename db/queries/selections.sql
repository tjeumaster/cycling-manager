-- name: get_squad_selection(squad_id)
SELECT c.id, c.first_name, c.last_name, c.team_id, c.price, 
    c.birth_date, c.nationality, c.image_url,
    t.name AS team_name, t.code AS team_code, 
    t.image_url AS team_image_url, ss.is_leader
FROM squad_selections ss
JOIN cyclists c ON ss.cyclist_id = c.id
JOIN teams t ON c.team_id = t.id
WHERE ss.squad_id = :squad_id;

-- name: insert_squad_selection(squad_id, cyclist_id, is_leader)!
INSERT INTO squad_selections (squad_id, cyclist_id, is_leader)
VALUES (:squad_id, :cyclist_id, :is_leader)
ON CONFLICT (squad_id, cyclist_id) DO 
UPDATE SET is_leader = EXCLUDED.is_leader;

-- name: delete_squad_selection_cyclist(squad_id, cyclist_id)!
DELETE FROM squad_selections
WHERE squad_id = :squad_id AND cyclist_id = :cyclist_id;

-- name: delete_squad_selection(squad_id)!
DELETE FROM squad_selections
WHERE squad_id = :squad_id;