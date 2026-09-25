"""
Analysis Module
Author: Meet Dodiya
Description: Statistical analysis and business insights generation
"""

import pandas as pd
import numpy as np
from scipy import stats


class BusinessAnalyzer:
    """
    Performs statistical analysis and generates business insights
    """
    
    def __init__(self, df):
        self.df = df
        self.insights = []
    
    def analyze_category_performance(self):
        """Analyze revenue and profitability by category"""
        category_analysis = self.df.groupby('category').agg({
            'revenue_after_discount': ['sum', 'mean', 'count'],
            'profit': ['sum', 'mean'],
            'profit_margin': 'mean'
        }).round(2)
        
        return category_analysis.sort_values(('revenue_after_discount', 'sum'), ascending=False)
    
    def analyze_regional_performance(self):
        """Analyze revenue by region"""
        regional_analysis = self.df.groupby('region').agg({
            'revenue_after_discount': ['sum', 'mean', 'count'],
            'profit': ['sum', 'mean'],
            'order_id': 'count'
        }).round(2)
        
        return regional_analysis.sort_values(('revenue_after_discount', 'sum'), ascending=False)
    
    def analyze_discount_impact(self):
        """Analyze impact of discounts on revenue and profit"""
        discount_analysis = self.df.groupby('has_discount').agg({
            'revenue_after_discount': ['sum', 'mean'],
            'profit': ['sum', 'mean'],
            'profit_margin': 'mean',
            'order_id': 'count'
        }).round(2)
        
        return discount_analysis
    
    def rfm_analysis(self):
        """
        Perform RFM (Recency, Frequency, Monetary) analysis
        """
        max_date = self.df['order_date'].max()
        
        rfm = self.df.groupby('customer_id').agg({
            'order_date': lambda x: (max_date - x.max()).days,
            'order_id': 'count',
            'revenue_after_discount': 'sum'
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Create quartile scores
        rfm['R_score'] = pd.qcut(rfm['recency'], q=4, labels=[4, 3, 2, 1], duplicates='drop')
        rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=4, 
                                labels=[1, 2, 3, 4], duplicates='drop')
        rfm['M_score'] = pd.qcut(rfm['monetary'], q=4, labels=[1, 2, 3, 4], duplicates='drop')
        
        rfm['RFM_Score'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)
        
        return rfm
    
    def segment_customers(self, rfm):
        """
        Segment customers based on RFM scores
        """
        def assign_segment(score):
            r, f, m = int(score[0]), int(score[1]), int(score[2])
            
            if r >= 3 and f >= 3 and m >= 3:
                return 'Champions'
            elif f >= 3 and m >= 3:
                return 'Loyal Customers'
            elif r >= 3 and (f >= 2 or m >= 2):
                return 'Potential Loyalists'
            elif r <= 2 and m >= 3:
                return 'At Risk'
            elif r <= 2 and f <= 2:
                return 'Need Attention'
            elif r >= 3:
                return 'New Customers'
            else:
                return 'Others'
        
        rfm['Segment'] = rfm['RFM_Score'].apply(assign_segment)
        return rfm
    
    def test_discount_impact(self):
        """
        Test if discount significantly impacts profit using t-test
        """
        no_discount = self.df[self.df['has_discount'] == 0]['profit']
        with_discount = self.df[self.df['has_discount'] == 1]['profit']
        
        t_stat, p_value = stats.ttest_ind(no_discount, with_discount)
        
        return {
            'no_discount_mean': no_discount.mean(),
            'with_discount_mean': with_discount.mean(),
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    
    def test_category_differences(self):
        """
        Test if revenue differs significantly across categories using ANOVA
        """
        categories = self.df['category'].unique()
        category_groups = [self.df[self.df['category'] == cat]['revenue_after_discount'].values 
                          for cat in categories]
        
        f_stat, p_value = stats.f_oneway(*category_groups)
        
        return {
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'categories': len(categories)
        }
    
    def correlation_analysis(self, columns):
        """
        Calculate correlation matrix for specified columns
        """
        return self.df[columns].corr()
    
    def seasonal_analysis(self):
        """
        Analyze seasonal patterns in revenue
        """
        seasonal = self.df.groupby('quarter').agg({
            'revenue_after_discount': ['sum', 'mean'],
            'profit': ['sum', 'mean'],
            'order_id': 'count'
        }).round(2)
        
        return seasonal
    
    def customer_concentration(self):
        """
        Analyze revenue concentration among customers
        """
        customer_revenue = self.df.groupby('customer_id')['revenue_after_discount'].sum().sort_values(ascending=False)
        total_revenue = customer_revenue.sum()
        
        top_10_pct = customer_revenue.head(int(len(customer_revenue) * 0.1)).sum()
        top_20_pct = customer_revenue.head(int(len(customer_revenue) * 0.2)).sum()
        
        return {
            'top_10_pct_revenue': top_10_pct,
            'top_10_pct_percentage': (top_10_pct / total_revenue) * 100,
            'top_20_pct_revenue': top_20_pct,
            'top_20_pct_percentage': (top_20_pct / total_revenue) * 100,
            'total_revenue': total_revenue,
            'concentration_ratio': top_10_pct / total_revenue
        }
    
    def generate_summary_report(self):
        """
        Generate comprehensive summary report
        """
        report = {
            'total_transactions': len(self.df),
            'unique_customers': self.df['customer_id'].nunique(),
            'date_range': f"{self.df['order_date'].min().date()} to {self.df['order_date'].max().date()}",
            'total_revenue': self.df['revenue_after_discount'].sum(),
            'total_profit': self.df['profit'].sum(),
            'avg_profit_margin': self.df['profit_margin'].mean(),
            'avg_customer_value': self.df.groupby('customer_id')['revenue_after_discount'].sum().mean(),
            'data_completeness': (1 - self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        }
        
        return report


if __name__ == "__main__":
    # Example usage
    from data_cleaning import generate_synthetic_ecommerce_data, DataCleaner
    
    print("Generating sample data...")
    df = generate_synthetic_ecommerce_data(n_records=5000)
    
    cleaner = DataCleaner(df)
    df_clean = cleaner.clean()
    
    # Add calculated columns
    df_clean['revenue'] = df_clean['quantity'] * df_clean['unit_price']
    df_clean['revenue_after_discount'] = df_clean['revenue'] * (1 - df_clean['discount'])
    df_clean['profit'] = df_clean['revenue_after_discount'] - (df_clean['quantity'] * df_clean['cost_price'])
    df_clean['profit_margin'] = (df_clean['profit'] / df_clean['revenue_after_discount'] * 100).fillna(0)
    df_clean['has_discount'] = (df_clean['discount'] > 0).astype(int)
    
    print("Performing analysis...")
    analyzer = BusinessAnalyzer(df_clean)
    
    # Test discount impact
    discount_test = analyzer.test_discount_impact()
    print(f"\nDiscount Impact Test:")
    print(f"  No Discount Mean Profit: ${discount_test['no_discount_mean']:.2f}")
    print(f"  With Discount Mean Profit: ${discount_test['with_discount_mean']:.2f}")
    print(f"  p-value: {discount_test['p_value']:.6f}")
    print(f"  Significant: {discount_test['significant']}")
    
    # RFM Analysis
    rfm = analyzer.rfm_analysis()
    rfm = analyzer.segment_customers(rfm)
    print(f"\nCustomer Segments:")
    print(rfm['Segment'].value_counts())
