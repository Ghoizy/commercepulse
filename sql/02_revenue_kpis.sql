-- Item price totals for DELIVERED orders. This is NOT net company revenue.
-- Revenue proxy excludes freight, refunds, tax, fees, and costs.
-- Do not join raw payments or raw reviews here: those can multiply item rows.
WITH delivered_order_values AS (
  SELECT
    o.order_id,
    substr(o.order_purchase_timestamp, 1, 7) AS purchase_month,
    SUM(i.price) AS merchandise_value_brl
  FROM orders o
  JOIN order_items i ON i.order_id = o.order_id
  WHERE o.order_status = 'delivered'
    AND o.order_purchase_timestamp IS NOT NULL
    AND i.price IS NOT NULL
    AND i.price >= 0
  GROUP BY o.order_id, substr(o.order_purchase_timestamp, 1, 7)
)
SELECT
  purchase_month,
  COUNT(*) AS delivered_orders_with_items,
  ROUND(SUM(merchandise_value_brl), 2) AS merchandise_value_brl,
  ROUND(AVG(merchandise_value_brl), 2) AS average_order_value_brl
FROM delivered_order_values
GROUP BY purchase_month
ORDER BY purchase_month;
