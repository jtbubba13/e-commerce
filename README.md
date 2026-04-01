# E-Commerce A/B Testing & Growth Analytics

## Overview
This project simulates a Shopify-style e-commerce environment to demonstrate end-to-end data analytics, experimentation, and business insight generation. 
It covers **A/B testing** to evaluate feature changes, **conversion funnel analysis** to identify drop-off points, and **Customer Acquisition Cost (CAC) modeling** to guide marketing efficiency. 
The goal is to showcase skills in **SQL, Python, statistical analysis, and business insights**—fully reproducible with synthetic data.

## Tech Stack
- **Database:** MySQL  
- **Data Processing:** Python (pandas, numpy, statsmodels)  
- **Data Visualization / Reporting:** Optional Power BI / Tableau  
- **Environment Management:** `.env` file for database credentials  
- **Version Control:** Git / GitHub  

## Dataset
Synthetic e-commerce dataset with the following tables:

| Table                    | Description                                                              |
|--------------------------|--------------------------------------------------------------------------|
| `users`                  | Customer information (signup date, country, device, acquisition channel) |
| `sessions`               | Session-level activity per user                                          |
| `products`               | Product catalog with category, price, cost                               |
| `events`                 | Funnel events (view_product, add_to_cart, purchase)                      |
| `orders`                 | Orders with revenue                                                      |
| `experiment_assignments` | A/B test assignment per user                                             |

All tables are generated and loaded via `generate_and_load.py`.

## Project Structure
```
ecommerce-ab-testing-project/
├── README.md
├── requirements.txt
├── .env.example
├── data/
├── scripts/
│   ├── data-generator.py
│   ├── ab-test-analysis.py
│   ├── funnel-analysis.py
│   └── cac-analysis.py
├── sql/
│   ├── schema.sql
├── notebooks/
├── dashboards/
└── reports/
```

## How to Run
1. **Setup database:**
```bash
mysql -u root -p < sql/schema.sql
```
2. **Create `.env` with DB credentials:**
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ecommerce_ab_testing
```
3. **Generate & load data:**
```bash
python scripts/data-generator.py
```
4. **Run analyses:**
```bash
python scripts/ab-test-analysis.py
python scripts/funnel-analysis.py
python scripts/cac-analysis.py
```

## Key Analyses
### A/B Testing
Experiment Example:
“Does adding product reviews increase conversion rate?”
Measured conversion rate differences between control and treatment groups, calculated lift, and statistical significance using a z-test. Sample output:

| Variant   | Sessions | Orders | Conversion Rate |
|-----------|----------|--------|-----------------|
| Control   | 1287     | 206    | 16.0%           |
| Treatment | 1234     | 191    | 15.4%           |

#### Lift: -3.30%
#### P-value: 0.7159
#### ❌ Not statistically significant

### Conversion Funnel Analysis
Tracked drop-offs from **views → add_to_cart → purchase**. Sample output:

| Stage        | Sessions | Drop-off Rate |
|--------------|----------|---------------|
| View Product | 2024     | –             |
| Add to Cart  | 807      | 39.87%        |
| Purchase     | 397      | 19.61%        |

### CAC Analysis
Ranked channels by cost per acquired customer (lower CAC = more efficient) and highlighted best/worst channels. Sample output:

| Channel     | Cost | Users | CAC  | Rank | Total Revenue | Profit    |
|-------------|------|-------|------|------|---------------|-----------|
| Email       | 300  | 249   | 1.20 | 1    | $9,305.13     | $9,005.13 |
| Organic     | 500  | 233   | 2.14 | 2    | $8,561.96     | $8,061.96 |
| Social      | 800  | 256   | 3.13 | 3    | $8,900.25     | $8,100.25 |
| Paid Search | 2000 | 262   | 7.63 | 4    | $9,906.62     | $7,906.62 |

🏆 **Best Channel (CAC):** Email  
⚠️ **Worst Channel (CAC):** Paid Search

💰 **Highest Profit:** Email  
💹 **Highest Revenue:** Paid Search

## Insights / Takeaways
- Product reviews in the treatment group decreased conversion by ~4%  
- Funnel analysis reveals the largest drop-off occurs at **View Product → Add to Cart**  
- Email marketing is the most efficient channel, guiding CAC optimization
- Email is also the most profitable channel whereas paid search generates the most revenue
- Framework can be adapted to real Shopify or Snowflake datasets

## Optional Next Steps
- Add **visualizations** using matplotlib, seaborn, or Tableau  
- ~~Implement **profit per channel analysis** to supplement CAC  (Done)~~
- Build a **dbt-style transformation pipeline** for real-world Snowflake integration

## License
MIT License – free for personal and portfolio use

## Contact
For questions or collaborations, reach out via [GitHub Profile / joshua_given@yahoo.com].

