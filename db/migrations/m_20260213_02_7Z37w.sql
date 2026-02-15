-- Make race_id column not nullable again
ALTER TABLE race_results 
ALTER COLUMN race_id SET NOT NULL;

-- Make cyclist_id column nullable to allow inserting results without a cyclist reference
ALTER TABLE race_results 
ALTER COLUMN cyclist_id DROP NOT NULL;