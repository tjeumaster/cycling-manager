-- name: insert_user(username, first_name, last_name, email, password_hash)$
INSERT INTO users (username, first_name, last_name, email, password_hash)
VALUES (:username, :first_name, :last_name, :email, :password_hash)
RETURNING id;

-- name: get_user_by_email(email)^
SELECT id, username, first_name, last_name, email, password_hash
FROM users
WHERE email = :email;
