CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    image_url VARCHAR(255) NOT NULL
);

CREATE TABLE cyclists (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    price FLOAT NOT NULL,
    birth_date DATE NOT NULL,
    nationality VARCHAR(255) NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    pcs_path VARCHAR(255),
    UNIQUE(first_name, last_name, team_id)
);

CREATE TABLE races (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    start_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    category VARCHAR(20) NOT NULL,
    pcs_path VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'planned',
    UNIQUE(name, year)
);

CREATE TABLE race_category_points (
    id SERIAL PRIMARY KEY,
    category VARCHAR(20) NOT NULL,
    position INTEGER NOT NULL,
    points INTEGER NOT NULL,
    UNIQUE(category, position)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE squads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE squad_cyclists (
    squad_id INTEGER NOT NULL REFERENCES squads(id) ON DELETE CASCADE,
    cyclist_id INTEGER NOT NULL REFERENCES cyclists(id) ON DELETE CASCADE,
    is_leader BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (squad_id, cyclist_id)
    -- Enforce a single leader per squad with a partial unique index below
);

CREATE TABLE competitions (
    id SERIAL PRIMARY KEY,
    invite_id UUID NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE competition_squads (
    competition_id INTEGER NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    squad_id INTEGER NOT NULL REFERENCES squads(id) ON DELETE CASCADE,
    PRIMARY KEY (competition_id, squad_id)
);

CREATE TABLE race_results (
    id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL REFERENCES races(id) ON DELETE CASCADE,
    position INTEGER,
    cyclist_id INTEGER NOT NULL REFERENCES cyclists(id) ON DELETE CASCADE,
    info VARCHAR(255)
);

CREATE TABLE squad_selections (
    id SERIAL PRIMARY KEY,
    squad_id INTEGER NOT NULL REFERENCES squads(id) ON DELETE CASCADE,
    cyclist_id INTEGER NOT NULL REFERENCES cyclists(id) ON DELETE CASCADE,
    is_leader BOOLEAN NOT NULL DEFAULT FALSE,
    is_selected BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(squad_id, cyclist_id)
    -- Enforce a single leader per squad with a partial unique index below
);

CREATE TABLE squad_race_selections (
    id SERIAL PRIMARY KEY,
    squad_id INTEGER NOT NULL REFERENCES squads(id) ON DELETE CASCADE,
    race_id INTEGER NOT NULL REFERENCES races(id) ON DELETE CASCADE,
    cyclist_id INTEGER NOT NULL REFERENCES cyclists(id) ON DELETE CASCADE,
    is_leader BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(squad_id, race_id, cyclist_id)
    -- Enforce a single leader per squad per race with a partial unique index below
);

CREATE TABLE squad_transfers (
    id SERIAL PRIMARY KEY,
    squad_id INTEGER NOT NULL REFERENCES squads(id) ON DELETE CASCADE,
    out_cyclist_id INTEGER NOT NULL REFERENCES cyclists(id) ON DELETE CASCADE,
    in_cyclist_id INTEGER NOT NULL REFERENCES cyclists(id) ON DELETE CASCADE,
    transfer_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Partial unique indexes to enforce single leaders where appropriate
CREATE UNIQUE INDEX IF NOT EXISTS uq_squad_cyclists_leader ON squad_cyclists (squad_id) WHERE is_leader = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS uq_squad_selections_leader ON squad_selections (squad_id) WHERE is_leader = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS uq_squad_race_selections_leader ON squad_race_selections (squad_id, race_id) WHERE is_leader = TRUE;
    



