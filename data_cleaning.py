"""
Data Cleaning Module
Author: Meet Dodiya
Description: Handles data loading, validation, and cleaning operations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataCleaner:
    """
    Handles all data cleaning and preprocessing operations
    """
    
    def __init__(self, df):
        self.df = df.copy()
        self.initial_shape = df.shape
        self.cleaning_log = []
    
    def remove_duplicates(self):
        """Remove duplicate rows from dataset"""
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        after = len(self.df)
        removed = before - after
        self.cleaning_log.append(f"Duplicates removed: {removed}")
        return removed
    
    def handle_missing_values(self, method='median'):
        """
        Handle missing values in numerical and categorical columns
        
        Args:
            method (str): 'median' for numerical, 'mode' for categorical
        """
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        
        # Handle numerical missing values
        for col in numerical_cols:
            if self.df[col].isnull().sum() > 0:
                missing_count = self.df[col].isnull().sum()
                if method == 'median':
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                elif method == 'mean':
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                self.cleaning_log.append(f"{col}: {missing_count} missing values filled")
        
        # Handle categorical missing values
        for col in categorical_cols:
            if self.df[col].isnull().sum() > 0:
                missing_count = self.df[col].isnull().sum()
                self.df[col].fillna(self.df[col].mode()[0], inplace=True)
                self.cleaning_log.append(f"{col}: {missing_count} missing values filled with mode")
    
    def convert_datatypes(self):
        """Convert columns to appropriate data types"""
        if 'order_date' in self.df.columns:
            self.df['order_date'] = pd.to_datetime(self.df['order_date'])
        self.cleaning_log.append("Date columns converted to datetime")
    
    def standardize_text(self):
        """Standardize text columns"""
        text_cols = self.df.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            if col not in ['product_name', 'customer_name']:
                self.df[col] = self.df[col].str.strip().str.title()
            else:
                self.df[col] = self.df[col].str.strip()
        
        self.cleaning_log.append("Text columns standardized")
    
    def remove_invalid_values(self):
        """Remove rows with impossible/invalid values"""
        before = len(self.df)
        
        # Remove negative quantities
        if 'quantity' in self.df.columns:
            self.df = self.df[self.df['quantity'] > 0]
        
        # Remove negative/zero prices
        if 'unit_price' in self.df.columns:
            self.df = self.df[self.df['unit_price'] > 0]
        
        # Validate discount range
        if 'discount' in self.df.columns:
            self.df = self.df[(self.df['discount'] >= 0) & (self.df['discount'] <= 1)]
        
        after = len(self.df)
        removed = before - after
        
        if removed > 0:
            self.cleaning_log.append(f"Invalid rows removed: {removed}")
        
        return removed
    
    def get_quality_report(self):
        """Generate data quality report"""
        print("="*60)
        print("DATA QUALITY REPORT")
        print("="*60)
        print(f"Initial shape: {self.initial_shape}")
        print(f"Final shape: {self.df.shape}")
        print(f"Rows removed: {self.initial_shape[0] - self.df.shape[0]}")
        print(f"Completeness: {((1 - self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100):.2f}%")
        print(f"\nCleaning Steps:")
        for step in self.cleaning_log:
            print(f"  - {step}")
        return self.df
    
    def clean(self):
        """Execute complete cleaning pipeline"""
        self.remove_duplicates()
        self.handle_missing_values()
        self.convert_datatypes()
        self.standardize_text()
        self.remove_invalid_values()
        return self.df


def generate_synthetic_ecommerce_data(n_records=15000, n_customers=3000, seed=42):
    """
    Generate realistic synthetic e-commerce dataset
    
    Args:
        n_records (int): Number of transactions
        n_customers (int): Number of unique customers
        seed (int): Random seed for reproducibility
    
    Returns:
        pd.DataFrame: Synthetic e-commerce dataset
    """
    
    np.random.seed(seed)
    
    # Define parameters
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
    regions = ['North', 'South', 'East', 'West']
    
    # Customer IDs
    customer_ids = np.random.choice(range(1, n_customers + 1), n_records)
    
    # Dates (spread across 5 years)
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days
    order_dates = [start_date + timedelta(days=np.random.randint(0, date_range)) 
                   for _ in range(n_records)]
    
    # Product details
    categories_list = np.random.choice(categories, n_records, p=[0.25, 0.30, 0.20, 0.15, 0.10])
    regions_list = np.random.choice(regions, n_records)
    
    # Pricing
    base_prices = {
        'Electronics': np.random.uniform(50, 500, n_records),
        'Clothing': np.random.uniform(20, 150, n_records),
        'Home & Garden': np.random.uniform(15, 200, n_records),
        'Sports': np.random.uniform(25, 300, n_records),
        'Books': np.random.uniform(10, 50, n_records)
    }
    
    unit_prices = np.array([base_prices[cat][i] for i, cat in enumerate(categories_list)])
    quantities = np.random.choice(range(1, 10), n_records, p=[0.35, 0.25, 0.15, 0.10, 0.07, 0.03, 0.02, 0.02, 0.01])
    
    # Cost (60-80% of price)
    cost_prices = unit_prices * np.random.uniform(0.60, 0.80, n_records)
    
    # Discounts (10% of transactions get discounts)
    discounts = np.where(np.random.random(n_records) < 0.10, 
                        np.random.uniform(0.05, 0.25, n_records), 
                        0)
    
    # Product names
    product_names = np.array([
        f"Product {np.random.randint(1, 100)}" for _ in range(n_records)
    ])
    
    # Create DataFrame
    df = pd.DataFrame({
        'order_id': range(1, n_records + 1),
        'customer_id': customer_ids,
        'product_id': np.random.randint(1, 500, n_records),
        'product_name': product_names,
        'category': categories_list,
        'region': regions_list,
        'order_date': order_dates,
        'quantity': quantities,
        'unit_price': np.round(unit_prices, 2),
        'cost_price': np.round(cost_prices, 2),
        'discount': np.round(discounts, 3)
    })
    
    # Add some missing values (5%)
    missing_rate = 0.05
    for col in ['quantity', 'discount']:
        missing_indices = np.random.choice(df.index, int(len(df) * missing_rate), replace=False)
        df.loc[missing_indices, col] = np.nan
    
    # Add some duplicates (0.5%)
    if len(df) > 100:
        n_duplicates = int(len(df) * 0.005)
        duplicate_indices = np.random.choice(df.index, n_duplicates, replace=False)
        df = pd.concat([df, df.iloc[duplicate_indices]], ignore_index=True)
    
    return df.sort_values('order_date').reset_index(drop=True)


if __name__ == "__main__":
    # Example usage
    print("Generating synthetic dataset...")
    df = generate_synthetic_ecommerce_data(n_records=15000)
    print(f"Dataset shape: {df.shape}")
    print(f"\nFirst few rows:\n{df.head()}")
    
    # Clean data
    print("\nCleaning data...")
    cleaner = DataCleaner(df)
    df_clean = cleaner.clean()
    cleaner.get_quality_report()
    
    # Save
    df_clean.to_csv('../data/raw/ecommerce_data.csv', index=False)
    print("\n✓ Dataset saved to data/raw/ecommerce_data.csv")
