WITH conversions AS (
    SELECT
        ea.variant,
        COUNT(DISTINCT s.session_id) AS sessions,
        COUNT(DISTINCT o.order_id) AS orders
    FROM sessions s
    JOIN experiment_assignments ea ON s.user_id = ea.user_id
    LEFT JOIN orders o ON s.session_id = o.session_id
    GROUP BY ea.variant
)

SELECT *,
       orders * 1.0 / sessions AS conversion_rate
FROM conversions;