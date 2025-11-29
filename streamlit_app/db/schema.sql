-- User table, simple login system with hashed PIN
CREATE TABLE IF NOT EXISTS player (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_game_id INTEGER NOT NULL UNIQUE,
    game_username TEXT NOT NULL UNIQUE,
    app_username TEXT,          -- for admin login only
    pin_hash TEXT,
    alliance TEXT,
    is_admin INTEGER NOT NULL DEFAULT 0,
    is_super_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL    -- "YYYY-MM-DDTHH:MM"
);

-- Activity table (e.g. Noble Advisor on Thursday)
CREATE TABLE IF NOT EXISTS activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    event_date TEXT,            -- "YYYY-MM-DD"
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL    -- "YYYY-MM-DDTHH:MM"
);

-- Availability per combination of player and activity
CREATE TABLE IF NOT EXISTS availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INT NOT NULL,
    activity_id INT NOT NULL,
    slot TEXT NOT NULL,         -- "HH:MM"
    created_at TEXT NOT NULL,   -- "YYYY-MM-DDTHH:MM"
    UNIQUE (player_id, activity_id, slot),
    FOREIGN KEY (player_id) REFERENCES player(player_id),
    FOREIGN KEY (activity_id) REFERENCES activity(id)
);
