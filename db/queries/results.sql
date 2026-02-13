-- name: insert_race_result(race_id, cyclist_id, position, info, cyclist_full_name)!
INSERT INTO race_results ( race_id, cyclist_id, position, info, cyclist_full_name)
VALUES ( :race_id, :cyclist_id, :position, :info, :cyclist_full_name )
ON CONFLICT (race_id, position) DO NOTHING;