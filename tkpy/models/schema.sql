CREATE TABLE IF NOT EXISTS lobbies (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gameworlds (
  id INTEGER PRIMARY KEY,
  gameworld_name TEXT NOT NULL,
  driver BLOB NOT NULL,
  lobby_id INTEGER NOT NULL,
  FOREIGN KEY (lobby_id) REFERENCES lobbies (id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);