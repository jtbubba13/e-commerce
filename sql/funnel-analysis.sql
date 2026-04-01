SELECT
    COUNT(DISTINCT CASE WHEN event_type = 'view_product' THEN session_id END) AS views,
    COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN session_id END) AS adds,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END) AS purchases
FROM events;