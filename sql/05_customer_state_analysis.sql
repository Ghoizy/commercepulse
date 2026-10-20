WITH ranked_reviews AS (
    SELECT
        order_id,
        review_score,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY review_creation_date DESC, review_id DESC
        ) AS rn
    FROM reviews
),

analysis_base AS (
    SELECT
        c.customer_state,
        CASE
            WHEN DATE(o.order_delivered_customer_date)
                 > DATE(o.order_estimated_delivery_date)
            THEN 'late'
            ELSE 'on_time'
        END AS delivery_group,
        CASE
            WHEN r.review_score <= 2 THEN 1
            ELSE 0
        END AS low_rating
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
)

SELECT
    customer_state,
    delivery_group,
    COUNT(*) AS reviewed_orders,
    ROUND(100.0 * AVG(low_rating), 2) AS pct_low_rating
FROM analysis_base
GROUP BY customer_state, delivery_group
HAVING COUNT(*) >= 30
ORDER BY customer_state, delivery_group;