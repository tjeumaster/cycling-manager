-- name: create_squad(name, user_id)^
INSERT INTO squads ( name, user_id)
VALUES (:name, :user_id)
ON CONFLICT (name) DO NOTHING
RETURNING id, name, user_id;

-- name: get_squads_by_user(user_id)
SELECT id, name, user_id
FROM squads
WHERE user_id = :user_id;

-- name: get_squad(squad_id)^
SELECT id, name, user_id
FROM squads
WHERE id = :squad_id;

-- name: get_squad_cyclists(squad_id, user_id)
SELECT c.id, c.first_name, c.last_name, c.team_id, c.price, 
    c.birth_date, c.nationality, c.image_url,
    t.name AS team_name, t.code AS team_code, 
    t.image_url AS team_image_url
FROM squad_cyclists sc
JOIN cyclists c ON sc.cyclist_id = c.id
JOIN squads s ON sc.squad_id = s.id
JOIN teams t ON c.team_id = t.id
WHERE s.id = :squad_id AND s.user_id = :user_id;

-- name: add_cyclist(squad_id, cyclist_id)!
INSERT INTO squad_cyclists (squad_id, cyclist_id)
VALUES (:squad_id, :cyclist_id);

-- name: remove_cyclist(squad_id, cyclist_id)!
DELETE FROM squad_cyclists
WHERE squad_id = :squad_id AND cyclist_id = :cyclist_id;

-- name: remove_cyclists(squad_id)!
DELETE FROM squad_cyclists
WHERE squad_id = :squad_id;

-- name: get_squad_price(squad_ids)$
SELECT SUM(c.price) as total_price
FROM cyclists c 
WHERE c.id = ANY(:squad_ids);





