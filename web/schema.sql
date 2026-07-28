CREATE TABLE IF NOT EXISTS review (
  id         TEXT PRIMARY KEY,   -- "crime/aakhri-call/part_01", stable across rebuilds
  status     TEXT NOT NULL,      -- approved | rejected | pending
  updated_at TEXT NOT NULL
);
