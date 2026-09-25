"""
Visualization Module
Author: Meet Dodiya
Description: Create professional visualizations for EDA insights
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd


class EDAVisualizer:
    """
    Create professional visualizations for exploratory data analysis
    """
    
    def __init__(self, df):
        self.df = df
        sns.set_style('whitegrid')
        sns.set_palette('husl')
        plt.rcParams['figure.figsize'] = (12, 6)
    
    def plot_missing_values(self, save_path=None):
        """Plot missing values distribution"""
        missing_data = (self.df.isnull().sum() / len(self.df) * 100).sort_values(ascending=False)
        missing_data = missing_data[missing_data > 0]
        
        if len(missing_data) == 0:
            print("No missing values to plot")
            return
        
        fig, ax = plt.subplots(figsize=(12, 5))
        missing_data.plot(kind='barh', color='coral', ax=ax)
        ax.set_xlabel('Missing Percentage (%)', fontsize=11, fontweight='bold')
        ax.set_title('Missing Values Distribution', fontsize=13, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_distributions(self, columns, save_path=None):
        """Plot distribution of numerical variables"""
        n_cols = len(columns)
        fig, axes = plt.subplots((n_cols + 1) // 2, 2, figsize=(14, 5 * ((n_cols + 1) // 2)))
        axes = axes.flatten()
        
        for idx, col in enumerate(columns):
            ax = axes[idx]
            ax.hist(self.df[col], bins=40, alpha=0.7, color='steelblue', edgecolor='black')
            ax.set_title(f'{col.upper()} Distribution', fontsize=11, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=10)
            ax.grid(alpha=0.3)
        
        # Remove extra subplots
        for idx in range(len(columns), len(axes)):
            fig.delaxes(axes[idx])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_category_performance(self, save_path=None):
        """Plot revenue by category"""
        category_revenue = self.df.groupby('category')['revenue_after_discount'].sum().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        category_revenue.plot(kind='barh', ax=ax, color='viridis')
        ax.set_xlabel('Total Revenue ($)', fontsize=11, fontweight='bold')
        ax.set_title('Revenue by Product Category', fontsize=13, fontweight='bold')
        
        for i, v in enumerate(category_revenue.values):
            ax.text(v + 5000, i, f'${v/1000:.0f}K', va='center', fontweight='bold')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_regional_performance(self, save_path=None):
        """Plot performance by region"""
        region_revenue = self.df.groupby('region')['revenue_after_discount'].sum().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        region_revenue.plot(kind='bar', ax=ax, color='coolwarm')
        ax.set_ylabel('Total Revenue ($)', fontsize=11, fontweight='bold')
        ax.set_title('Revenue by Region', fontsize=13, fontweight='bold')
        ax.set_xticklabels(region_revenue.index, rotation=45)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_discount_impact(self, save_path=None):
        """Plot impact of discounts on profit\"\"\"
        discount_impact = self.df.groupby('has_discount').agg({\n            'revenue_after_discount': 'sum',\n            'profit': 'sum'\n        })\n        \n        fig, ax = plt.subplots(figsize=(10, 6))\n        \n        x = np.arange(len(discount_impact))\n        width = 0.35\n        \n        ax.bar(x - width/2, discount_impact['revenue_after_discount'], width, \n               label='Revenue', color='steelblue')\n        ax.bar(x + width/2, discount_impact['profit'], width, \n               label='Profit', color='coral')\n        \n        ax.set_ylabel('Amount ($)', fontsize=11, fontweight='bold')\n        ax.set_title('Impact of Discounts on Revenue and Profit', fontsize=13, fontweight='bold')\n        ax.set_xticks(x)\n        ax.set_xticklabels(['No Discount', 'With Discount'])\n        ax.legend()\n        ax.grid(alpha=0.3, axis='y')\n        \n        plt.tight_layout()\n        if save_path:\n            plt.savefig(save_path, dpi=300, bbox_inches='tight')\n        plt.show()\n    \n    def plot_correlation_heatmap(self, columns, save_path=None):\n        \"\"\"Plot correlation heatmap\"\"\"\n        correlation_matrix = self.df[columns].corr()\n        \n        fig, ax = plt.subplots(figsize=(10, 8))\n        sns.heatmap(correlation_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,\n                    square=True, linewidths=1, cbar_kws={\"shrink\": 0.8}, ax=ax)\n        ax.set_title('Correlation Matrix - Key Business Metrics', fontsize=13, fontweight='bold', pad=20)\n        \n        plt.tight_layout()\n        if save_path:\n            plt.savefig(save_path, dpi=300, bbox_inches='tight')\n        plt.show()\n    \n    def plot_time_series(self, column, save_path=None):\n        \"\"\"Plot time series of revenue or profit\"\"\"\n        monthly_data = self.df.groupby(self.df['order_date'].dt.to_period('M'))[column].sum()\n        monthly_data.index = monthly_data.index.to_timestamp()\n        \n        fig, ax = plt.subplots(figsize=(14, 6))\n        ax.plot(monthly_data.index, monthly_data.values, marker='o', linewidth=2, markersize=6)\n        ax.fill_between(monthly_data.index, monthly_data.values, alpha=0.3)\n        ax.set_xlabel('Date', fontsize=11, fontweight='bold')\n        ax.set_ylabel(f'{column.capitalize()} ($)', fontsize=11, fontweight='bold')\n        ax.set_title(f'Monthly {column.capitalize()} Trend', fontsize=13, fontweight='bold')\n        ax.grid(alpha=0.3)\n        \n        plt.tight_layout()\n        if save_path:\n            plt.savefig(save_path, dpi=300, bbox_inches='tight')\n        plt.show()\n    \n    def plot_outliers_boxplot(self, columns, save_path=None):\n        \"\"\"Plot box plots for outlier detection\"\"\"\n        n_cols = len(columns)\n        fig, axes = plt.subplots((n_cols + 1) // 2, 2, figsize=(14, 5 * ((n_cols + 1) // 2)))\n        axes = axes.flatten()\n        \n        for idx, col in enumerate(columns):\n            ax = axes[idx]\n            bp = ax.boxplot([self.df[col]], vert=True, patch_artist=True, widths=0.5)\n            bp['boxes'][0].set_facecolor('lightblue')\n            bp['boxes'][0].set_alpha(0.7)\n            \n            ax.set_ylabel(col, fontsize=11, fontweight='bold')\n            ax.set_title(f'{col.upper()} - Outlier Detection', fontweight='bold')\n            ax.grid(alpha=0.3, axis='y')\n        \n        for idx in range(len(columns), len(axes)):\n            fig.delaxes(axes[idx])\n        \n        plt.tight_layout()\n        if save_path:\n            plt.savefig(save_path, dpi=300, bbox_inches='tight')\n        plt.show()\n    \n    def plot_customer_segments(self, rfm, save_path=None):\n        \"\"\"Plot customer segmentation results\"\"\"\n        fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n        \n        # Segment distribution\n        segment_counts = rfm['Segment'].value_counts()\n        colors = plt.cm.Set3(range(len(segment_counts)))\n        axes[0].pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%',\n                   colors=colors, startangle=90)\n        axes[0].set_title('Customer Distribution by Segment', fontweight='bold')\n        \n        # Segment monetary value\n        segment_monetary = rfm.groupby('Segment')['monetary'].sum().sort_values(ascending=False)\n        axes[1].bar(range(len(segment_monetary)), segment_monetary.values, color='Set2')\n        axes[1].set_xticks(range(len(segment_monetary)))\n        axes[1].set_xticklabels(segment_monetary.index, rotation=45, ha='right')\n        axes[1].set_ylabel('Total Revenue ($)', fontweight='bold')\n        axes[1].set_title('Revenue Contribution by Segment', fontweight='bold')\n        \n        plt.tight_layout()\n        if save_path:\n            plt.savefig(save_path, dpi=300, bbox_inches='tight')\n        plt.show()\n    \n    def create_interactive_dashboard(self, output_file='dashboard.html'):\n        \"\"\"Create interactive Plotly dashboard\"\"\"\n        # Revenue by category\n        fig1 = px.bar(self.df.groupby('category')['revenue_after_discount'].sum().reset_index(),\n                     x='category', y='revenue_after_discount',\n                     title='Revenue by Category',\n                     labels={'revenue_after_discount': 'Revenue ($)', 'category': 'Category'})\n        \n        # Revenue trend\n        monthly = self.df.groupby(self.df['order_date'].dt.to_period('M'))['revenue_after_discount'].sum().reset_index()\n        monthly['order_date'] = monthly['order_date'].astype(str)\n        fig2 = px.line(monthly, x='order_date', y='revenue_after_discount',\n                      title='Monthly Revenue Trend',\n                      labels={'revenue_after_discount': 'Revenue ($)', 'order_date': 'Month'})\n        \n        # Discount impact\n        discount_data = self.df.groupby('has_discount')['profit_margin'].mean().reset_index()\n        discount_data['has_discount'] = discount_data['has_discount'].map({0: 'No Discount', 1: 'With Discount'})\n        fig3 = px.bar(discount_data, x='has_discount', y='profit_margin',\n                     title='Profit Margin by Discount Status',\n                     labels={'profit_margin': 'Profit Margin (%)', 'has_discount': 'Status'})\n        \n        return fig1, fig2, fig3


def create_summary_report(df, analyzer, output_path='reports/summary_report.txt'):\n    \"""Generate comprehensive summary report\"\"\"\n    report = analyzer.generate_summary_report()\n    \n    with open(output_path, 'w') as f:\n        f.write(\"=\"*70 + \"\\n\")\n        f.write(\"E-COMMERCE ANALYTICS - EXECUTIVE SUMMARY\\n\")\n        f.write(\"=\"*70 + \"\\n\\n\")\n        \n        for key, value in report.items():\n            f.write(f\"{key.replace('_', ' ').title():.<40} {value}\\n\")\n    \n    print(f\"✓ Summary report saved to {output_path}\")\n\n\nif __name__ == \"__main__\":\n    # Example usage\n    from data_cleaning import generate_synthetic_ecommerce_data, DataCleaner\n    \n    print(\"Generating sample data...\")\n    df = generate_synthetic_ecommerce_data(n_records=5000)\n    \n    cleaner = DataCleaner(df)\n    df_clean = cleaner.clean()\n    \n    # Add calculated columns\n    df_clean['revenue'] = df_clean['quantity'] * df_clean['unit_price']\n    df_clean['revenue_after_discount'] = df_clean['revenue'] * (1 - df_clean['discount'])\n    df_clean['profit'] = df_clean['revenue_after_discount'] - (df_clean['quantity'] * df_clean['cost_price'])\n    df_clean['profit_margin'] = (df_clean['profit'] / df_clean['revenue_after_discount'] * 100).fillna(0)\n    \n    print(\"Creating visualizations...\")\n    visualizer = EDAVisualizer(df_clean)\n    visualizer.plot_category_performance()\n    visualizer.plot_regional_performance()\n    visualizer.plot_discount_impact()\n """