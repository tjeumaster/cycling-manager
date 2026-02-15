-- name: insert_competition(name, created_by)!
INSERT INTO competitions (invite_id, name, created_by) 
VALUES (gen_random_uuid(), :name, :created_by)
ON CONFLICT (name) DO NOTHING;

-- name: get_competitions_by_user(user_id)
SELECT id, name, created_by
FROM competitions
WHERE created_by = :user_id;

-- name: get_competition_by_name(name)
SELECT id, name, created_by
FROM competitions
WHERE name = :name;
