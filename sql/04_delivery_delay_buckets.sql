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

delivery_data AS (
    SELECT
        o.order_id,
        CAST(
            julianday(date(o.order_delivered_customer_date))
            - julianday(date(o.order_estimated_delivery_date))
            AS INTEGER
        ) AS days_late,
        r.review_score
    FROM orders o
    LEFT JOIN ranked_reviews r
        ON o.order_id = r.order_id
        AND r.rn = 1
    WHERE o.order_status = 'delivered'
        AND date(o.order_delivered_customer_date) IS NOT NULL
        AND date(o.order_estimated_delivery_date) IS NOT NULL
),

categorized AS (
    SELECT
        CASE
            WHEN days_late <= -7 THEN '01_Early 7+ days'
            WHEN days_late BETWEEN -6 AND -1 THEN '02_Early 1-6 days'
            WHEN days_late = 0 THEN '03_On estimated date'
            WHEN days_late BETWEEN 1 AND 3 THEN '04_Late 1-3 days'
            WHEN days_late BETWEEN 4 AND 7 THEN '05_Late 4-7 days'
            ELSE '06_Late 8+ days'
        END AS delivery_category,
        review_score
    FROM delivery_data
)

SELECT
    delivery_category,
    COUNT(*) AS total_orders,
    COUNT(review_score) AS reviewed_orders,
    ROUND(AVG(review_score), 2) AS avg_rating,
    ROUND(
        100.0 * SUM(
            CASE WHEN review_score <= 2 THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(review_score), 0),
        2
    ) AS pct_low_rating
FROM categorized
GROUP BY delivery_category
ORDER BY delivery_category;