-- Run first. Check join keys and potential multiplicity before computing KPIs.
SELECT
  (SELECT COUNT(*) FROM orders) AS n_orders,
  (SELECT COUNT(DISTINCT order_id) FROM orders) AS n_unique_orders,
  (SELECT COUNT(*) FROM order_items) AS n_items,
  (SELECT COUNT(*) FROM customers) AS n_customer_records,
  (SELECT COUNT(*) FROM reviews) AS n_reviews,
  (SELECT COUNT(*) FROM orders o LEFT JOIN customers c ON c.customer_id = o.customer_id WHERE c.customer_id IS NULL) AS orders_without_customer,
  (SELECT COUNT(*) FROM order_items i LEFT JOIN orders o ON o.order_id = i.order_id WHERE o.order_id IS NULL) AS items_without_order,
  (SELECT COUNT(*) FROM order_items WHERE price IS NULL OR price < 0) AS invalid_item_prices,
  (SELECT COUNT(*) FROM (SELECT order_id FROM reviews GROUP BY order_id HAVING COUNT(*) > 1)) AS orders_with_multiple_reviews;
