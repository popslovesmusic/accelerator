SELECT * FROM decisions ORDER BY payload_bytes DESC LIMIT 20;
SELECT json_path,SUM(exclusive_bytes) AS bytes FROM json_nodes GROUP BY json_path ORDER BY bytes DESC LIMIT 100;
SELECT value_hash,COUNT(*) FROM json_nodes WHERE value_hash IS NOT NULL GROUP BY value_hash HAVING COUNT(*)>1;
SELECT * FROM large_strings ORDER BY string_bytes DESC LIMIT 100;
