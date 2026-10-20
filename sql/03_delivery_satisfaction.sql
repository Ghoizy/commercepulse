-- One observation per delivered order, with at most one review.
-- If multiple reviews exist, choose the latest review_creation_date, then review_id.
-- Comparing late vs on-time ratings measures association, not causation.
WITH ranked_reviews AS (
  SELECT
    order_id, review_id, review_score,
    ROW_NUMBER() OVER (
      PARTITION BY order_id
      ORDER BY review_creation_date DESC, review_id DESC
    ) AS rn
  FROM reviews
), eligible_orders AS (
  SELECT
    o.order_id,
    CASE WHEN date(o.order_delivered_customer_date) > date(o.order_estimated_delivery_date)
         THEN 'late' ELSE 'on_time_or_early' END AS delivery_group,
    r.review_score
  FROM orders o
  LEFT JOIN ranked_reviews r ON r.order_id = o.order_id AND r.rn = 1
  WHERE o.order_status = 'delivered'
    AND date(o.order_delivered_customer_date) IS NOT NULL
    AND date(o.order_estimated_delivery_date) IS NOT NULL
)
SELECT
  delivery_group,
  COUNT(*) AS orders_with_valid_delivery_dates,
  COUNT(review_score) AS orders_with_review,
  ROUND(AVG(review_score), 3) AS mean_review_score,
  SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) AS low_ratings,
  ROUND(100.0 * SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) /
    NULLIF(COUNT(review_score), 0), 2) AS pct_low_rating_among_reviewed_orders
FROM eligible_orders
GROUP BY delivery_group
ORDER BY delivery_group;
