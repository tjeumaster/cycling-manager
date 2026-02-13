-- Add cyclist_full_name column to store the full name of the cyclist for easier reference
ALTER TABLE race_results ADD COLUMN cyclist_full_name VARCHAR(255);

-- Make race_id column nullable to allow inserting results without a cyclist reference
ALTER TABLE race_results ALTER COLUMN race_id DROP NOT NULL;