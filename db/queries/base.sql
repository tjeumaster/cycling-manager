-- name: insert_team(name, code, image_url)!
INSERT INTO teams (name, code, image_url) 
VALUES (:name, :code, :image_url)
ON CONFLICT (code) DO NOTHING;

-- name: insert_cyclist(first_name, last_name, team_id, price, birth_date, nationality, image_url, pcs_path)!
INSERT INTO cyclists (
    first_name, last_name, team_id, price, 
    birth_date, nationality, image_url, pcs_path
) 
VALUES (
    :first_name, :last_name, :team_id, :price, 
    :birth_date, :nationality, :image_url, :pcs_path
)
ON CONFLICT (first_name, last_name, team_id) DO NOTHING;

-- name: get_cyclists()
SELECT 
    c.id, c.first_name, c.last_name, c.team_id, c.price, 
    c.birth_date, c.nationality, c.image_url,
    t.name AS team_name, t.code AS team_code, 
    t.image_url AS team_image_url
FROM cyclists c
JOIN teams t ON c.team_id = t.id;

-- name: get_teams()
SELECT id, name, code, image_url 
FROM teams; 

-- name: get_cyclist_by_id(id)
SELECT 
    c.id, c.first_name, c.last_name, c.team_id, c.price, 
    c.birth_date, c.nationality, c.image_url,
    t.name AS team_name, t.code AS team_code, 
    t.image_url AS team_image_url
FROM cyclists c
JOIN teams t ON c.team_id = t.id
WHERE c.id = :id;

-- name: insert_race(name, year, start_timestamp, category, pcs_path, status)!
INSERT INTO races (
    name, year, start_timestamp, category, pcs_path, status
) VALUES (
    :name, :year, :start_timestamp, :category, :pcs_path, :status
)
ON CONFLICT (name, year) DO NOTHING;

-- name: update_race_status(id, status)!
UPDATE races
SET status = :status
WHERE id = :id;

-- name: get_races()
SELECT id, name, year, start_timestamp, category, pcs_path, status
FROM races
ORDER BY start_timestamp;

-- name: insert_race_category_points(category, position, points)!
INSERT INTO race_category_points (category, position, points)
VALUES (:category, :position, :points)
ON CONFLICT (category, position) DO NOTHING;

-- name: get_pcs_races()
SELECT id, name, year, start_timestamp, category, pcs_path, status
FROM races
WHERE pcs_path IS NOT NULL AND status = 'planned';