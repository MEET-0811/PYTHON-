"""
Configuration Module
Author: Meet Dodiya
Project: InsightFlow - E-Commerce Analytics
Description: Centralized configuration for the project
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Data paths
DATA_RAW = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED = PROJECT_ROOT / 'data' / 'processed'
NOTEBOOKS = PROJECT_ROOT / 'notebooks'
REPORTS = PROJECT_ROOT / 'reports'
FIGURES = REPORTS / 'figures'
SRC = PROJECT_ROOT / 'src'

# Ensure directories exist
for directory in [DATA_RAW, DATA_PROCESSED, NOTEBOOKS, REPORTS, FIGURES, SRC]:
    directory.mkdir(parents=True, exist_ok=True)

# Dataset configuration
DATASET_CONFIG = {
    'n_records': 15000,
    'n_customers': 3000,
    'date_range': ('2019-01-01', '2024-12-31'),
    'categories': ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books'],
    'regions': ['North', 'South', 'East', 'West'],
    'random_seed': 42
}

# Analysis configuration
ANALYSIS_CONFIG = {
    'test_significance_level': 0.05,
    'rfm_quartiles': 4,
    'outlier_method': 'IQR',
    'outlier_iqr_multiplier': 1.5
}

# Visualization configuration
VISUALIZATION_CONFIG = {
    'style': 'whitegrid',
    'palette': 'husl',
    'figure_dpi': 300,
    'default_figsize': (12, 6),
    'color_palette': 'viridis'
}

# Segmentation configuration
SEGMENTATION_CONFIG = {
    'segments': {
        'Champions': {'recency': (3, 4), 'frequency': (3, 4), 'monetary': (3, 4)},
        'Loyal Customers': {'frequency': (3, 4), 'monetary': (3, 4)},
        'Potential Loyalists': {'recency': (3, 4)},
        'At Risk': {'recency': (0, 2), 'monetary': (3, 4)},
        'Need Attention': {'recency': (0, 2), 'frequency': (0, 2)},
        'New Customers': {'recency': (3, 4)}
    }
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Project metadata
PROJECT_METADATA = {
    'name': 'InsightFlow',
    'description': 'Advanced E-Commerce Customer & Sales Analytics',
    'version': '1.0.0',
    'author': 'Meet Dodiya',
    'license': 'MIT',
    'url': 'https://github.com/meetdodiya/ecommerce-customer-analytics'
}

# Business KPIs to track
KPI_TRACKING = {
    'revenue_metrics': ['total_revenue', 'avg_order_value', 'revenue_per_customer'],
    'profit_metrics': ['total_profit', 'profit_margin', 'profit_per_customer'],
    'customer_metrics': ['total_customers', 'repeat_purchase_rate', 'customer_lifetime_value'],
    'discount_metrics': ['discount_percentage', 'discount_impact_on_margin'],
    'regional_metrics': ['revenue_by_region', 'growth_by_region'],
    'category_metrics': ['revenue_by_category', 'profit_by_category']
}

if __name__ == '__main__':
    print("Configuration loaded successfully")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data path: {DATA_RAW}")
    print(f"Reports path: {REPORTS}")
