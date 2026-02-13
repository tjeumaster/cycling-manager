-- Add unique constraint on race_results to prevent duplicate entries
ALTER TABLE race_results ADD CONSTRAINT unique_race_cyclist UNIQUE (race_id, position);