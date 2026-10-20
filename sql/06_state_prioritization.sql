WITH ranked_reviews AS (
    SELECT
        order_id,
        review_score,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY review_creation_date DESC,
                     review_id DESC
        ) AS rn
    FROM reviews
),

analysis_base AS (
    SELECT
        c.customer_state,
        CASE
            WHEN DATE(o.order_delivered_customer_date)
               > DATE(o.order_estimated_delivery_date)
            THEN 1 ELSE 0
        END AS is_late,
        CASE
            WHEN r.review_score <= 2 THEN 1
            ELSE 0
        END AS is_low_rating
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    JOIN ranked_reviews r
        ON o.order_id = r.order_id
       AND r.rn = 1
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
      AND r.review_score IS NOT NULL
),

state_stats AS (
    SELECT
        customer_state,
        COUNT(*) AS total_reviewed_orders,

        SUM(is_late) AS late_orders,

        SUM(CASE WHEN is_late = 0
            THEN 1 ELSE 0 END) AS on_time_orders,

        SUM(CASE WHEN is_late = 1
                  AND is_low_rating = 1
            THEN 1 ELSE 0 END) AS late_low_ratings,

        SUM(CASE WHEN is_late = 0
                  AND is_low_rating = 1
            THEN 1 ELSE 0 END) AS on_time_low_ratings
    FROM analysis_base
    GROUP BY customer_state
)

SELECT
    customer_state,
    total_reviewed_orders,
    late_orders,

    ROUND(
        100.0 * late_orders
        / NULLIF(total_reviewed_orders, 0),
        2
    ) AS pct_late,

    late_low_ratings,

    ROUND(
        100.0 * late_low_ratings
        / NULLIF(late_orders, 0),
        2
    ) AS pct_low_late,

    ROUND(
        100.0 * on_time_low_ratings
        / NULLIF(on_time_orders, 0),
        2
    ) AS pct_low_on_time

FROM state_stats

WHERE late_orders >= 30
  AND on_time_orders >= 30

ORDER BY late_low_ratings DESC
LIMIT 10;
