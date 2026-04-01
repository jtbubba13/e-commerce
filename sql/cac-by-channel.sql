WITH spend AS (
    SELECT 'paid_search' AS channel, 2000 AS cost UNION
    SELECT 'organic', 500 UNION
    SELECT 'email', 300 UNION
    SELECT 'social', 800
),

acquisitions AS (
    SELECT acquisition_channel, COUNT(DISTINCT user_id) AS users
    FROM users
    GROUP BY acquisition_channel
)

SELECT
    a.acquisition_channel,
    s.cost,
    a.users,
    s.cost / a.users AS cac
FROM acquisitions a
JOIN spend s ON a.acquisition_channel = s.channel;