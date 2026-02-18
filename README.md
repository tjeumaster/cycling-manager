# cycling-manager

A small management tool for cycling races, teams and riders.

## Overview

This project stores simple models and repositories to manage cycling-related data (races, cyclists, teams) and provides sync tooling and routers for integration.

Core responsibilities:
- Define data models using `pydantic` (`models/`).
- Persist and load data via `db/` and repository helpers (`repositories/`).
- Provide sync operations in `services/` and HTTP-like routing in `routers/`.

## Project layout

- `main.py` — application entry point.
- `config.py` — configuration values.
- `data/` — sample JSON fixtures (`cyclists.json`, `points.json`, `races.json`).
- `db/` — database helpers, loader and migrations (Yoyo migrations present).
- `models/` — `Race`, `Cyclist`, `Team` and related Pydantic models.
- `repositories/` — repository abstractions for DB access.
- `routers/` — routing layer used by the application.
- `services/` — business logic and synchronization tasks.

## Architecture

```mermaid
flowchart LR
    Main["main.py\n(entry)"] --> Routers["routers/\n(route layer)"]
    Routers --> Services["services/\n(business logic)"]
    Services --> Repos["repositories/\n(DB access)"]
    Repos --> DB["db/\n(database + migrations)"]
    Data["data/\n(fixtures)"] --> Loader["db/loader.py"] --> DB
    subgraph Models["models/"]
        ModelsEntities["Race, Cyclist, Team\n(Pydantic models)"]
    end
    ModelsEntities --> Repos
    ModelsEntities --> Services
```

## Database Schema

The diagram below shows the main tables and their relationships (based on `db/migrations`).

```mermaid
erDiagram
    TEAMS {
        int id PK
        string code
        string name
        string image_url
    }

    CYCLISTS {
        int id PK
        string first_name
        string last_name
        int team_id FK
        float price
        date birth_date
        string nationality
        string image_url
        string pcs_path
    }

    RACES {
        int id PK
        string name
        int year
        datetime start_timestamp
        string category
        string pcs_path
        string status
    }

    RACE_CATEGORY_POINTS {
        int id PK
        string category
        int position
        int points
    }

    USERS {
        int id PK
        string username
        string first_name
        string last_name
        string email
    }

    SQUADS {
        int id PK
        int user_id FK
        string name
        datetime created_on
        datetime updated_on
    }

    SQUAD_CYCLISTS {
        int squad_id FK
        int cyclist_id FK
    }

    COMPETITIONS {
        int id PK
        uuid invite_id
        string name
        int created_by FK
    }

    COMPETITION_SQUADS {
        int competition_id FK
        int squad_id FK
    }

    RACE_RESULTS {
        int id PK
        int race_id FK
        int position
        int cyclist_id FK
        string info
        string cyclist_full_name
    }

    SQUAD_SELECTIONS {
        int id PK
        int squad_id FK
        int cyclist_id FK
        bool is_leader
        bool is_selected
    }

    SQUAD_RACE_SELECTIONS {
        int id PK
        int squad_id FK
        int race_id FK
        int cyclist_id FK
        bool is_leader
    }

    SQUAD_TRANSFERS {
        int id PK
        int squad_id FK
        int out_cyclist_id FK
        int in_cyclist_id FK
        datetime transfer_timestamp
    }

    RACE_CYCLISTS {
        int race_id FK
        int cyclist_id FK
    }

    TEAMS ||--o{ CYCLISTS : has
    USERS ||--o{ SQUADS : owns
    SQUADS ||--o{ SQUAD_CYCLISTS : contains
    CYCLISTS ||--o{ SQUAD_CYCLISTS : member
    COMPETITIONS ||--o{ COMPETITION_SQUADS : includes
    SQUADS ||--o{ COMPETITION_SQUADS : participates
    RACES ||--o{ RACE_RESULTS : has
    CYCLISTS ||--o{ RACE_RESULTS : rider
    RACES ||--o{ RACE_CYCLISTS : includes
    CYCLISTS ||--o{ RACE_CYCLISTS : participates
    SQUADS ||--o{ SQUAD_SELECTIONS : selects
    CYCLISTS ||--o{ SQUAD_SELECTIONS : selectable
    SQUADS ||--o{ SQUAD_RACE_SELECTIONS : selects_for_race
    RACES ||--o{ SQUAD_RACE_SELECTIONS : race
    CYCLISTS ||--o{ SQUAD_RACE_SELECTIONS : cyclist
    SQUADS ||--o{ SQUAD_TRANSFERS : has_transfers
    CYCLISTS ||--o{ SQUAD_TRANSFERS : involved
    USERS ||--o{ COMPETITIONS : created

    RACE_CATEGORY_POINTS ||..|| RACES : category
    RACE_CATEGORY_POINTS ||..|| RACE_RESULTS : position

    %% Notes: partial unique indexes enforce single leaders on squads/selections.

```
