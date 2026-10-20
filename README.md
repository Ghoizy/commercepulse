# CommercePulse — E-Commerce Revenue & Customer Experience Intelligence

> **Status:** Completed portfolio case study.
> SQL analysis, statistical testing,
> interactive dashboard, and executive report.

## Business questions

1. How much **merchandise value** is associated with delivered orders each month?
2. What is the average value of a delivered order?
3. How often are deliveries late compared with their estimated delivery dates?
4. Is late delivery **associated** with lower customer review scores?
5. Which operational segments should be prioritized for further investigation? (future work)

## Dataset

**Olist Brazilian E-Commerce Public Dataset by Olist** (approx. 100k orders from 2016–2018).

Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce  
License listed by publisher: **CC BY-NC-SA 4.0**. Attribute the data source and respect the license. The data files are not included in this repository.

The historical Brazilian dataset is used to demonstrate analytical skills, not to make claims about current e-commerce conditions or to represent a real Olist engagement.

## Getting started (Windows / VS Code)

1. Download the dataset from the Kaggle link above.
2. Extract **these four CSV files** into `data/raw/`:
   - `olist_orders_dataset.csv`
   - `olist_order_items_dataset.csv`
   - `olist_customers_dataset.csv`
   - `olist_order_reviews_dataset.csv`
3. Open the project folder in VS Code and its terminal.
4. Run:

```powershell
py -3.12 src/load_data.py
py -3.12 src/run_queries.py
```

No external Python libraries are needed for the data loader and SQL reports; they use Python's built-in `sqlite3` module. To run the exploratory statistical association test:

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 src/stats_delivery.py
```

The local SQLite database is generated at `data/processed/commercepulse.sqlite` and ignored by Git.

## Files

```text
src/load_data.py                 # Parse raw CSV into local SQLite tables
src/run_queries.py               # Run and print SQL outputs
src/stats_delivery.py            # Chi-square association test; interpret carefully
sql/01_data_quality.sql         # Check source counts and key issues
sql/02_revenue_kpis.sql          # Order-grain monthly merchandise metrics
sql/03_delivery_satisfaction.sql # Compare delay groups & review scores
docs/project_brief.md           # Project scope and definitions
docs/roadmap_14_days.md         # Guided sequence
```

## Metric contracts (important)

- **Merchandise value:** Sum of `order_items.price` for *delivered orders*. Excludes freight, refunds, taxes, fees, costs. It is **not actual Olist company net revenue, gross profit, or GMV in a formal financial sense**.
- **AOV proxy:** Merchandise value divided by number of delivered orders with valid item prices.
- **Late delivery:** actual delivery calendar date later than estimated calendar date. Only delivered orders with both valid timestamps.
- **Low-rating rate:** proportion of reviewed orders with score 1 or 2, among orders with a valid review score. Not all orders have reviews.
- **Review deduplication:** at most one review per order (latest creation date, then review ID) when comparing delivery and satisfaction.
- **Statistical analysis:** an association test is not evidence that delay *causes* poor ratings. Consider selection bias, geography, categories, delivery duration, and other confounders.

## Roadmap and presentation

The first milestone is a reproducible SQL analysis with correct join grains and explicitly defined KPIs. Later milestones include deeper statistical intervals, segment-level analysis, a dashboard, a decision memo, and publishing evidence to GitHub and LinkedIn.

**Author:** Add your preferred name and GitHub profile after initial validation.
