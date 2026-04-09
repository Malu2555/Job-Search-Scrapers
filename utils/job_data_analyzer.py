''' This module provides tools for analyzing the data scientist job market 
using the collected job listings data.It Includes extensive data Visualizations
 and insights on demand vs supply, salary trends, and market competition.'''

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from collections import Counter
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class JobMarketAnalyzer:
    def __init__(self, data_file=None):
        self.df = None
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, file_path):
        """Load job data from CSV"""
        try:
            self.df = pd.read_csv(file_path)
            print(f"Loaded {len(self.df)} job listings")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_sample_data(self):
        """Create sample data for demonstration"""
        np.random.seed(42)
        n_samples = 1000
        
        # Sample locations with realistic distribution
        locations = ['San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX', 
                    'Boston, MA', 'Denver, CO', 'Chicago, IL', 'Washington, DC',
                    'Los Angeles, CA', 'Remote'] * 100
        
        # Job titles with realistic distribution
        titles = (['Data Scientist'] * 400 + ['Senior Data Scientist'] * 200 + 
                 ['Machine Learning Engineer'] * 150 + ['Data Analyst'] * 150 +
                 ['AI Research Scientist'] * 100)
        
        # Generate sample data
        data = {
            'title': np.random.choice(titles, n_samples),
            'company': [f'Company_{i}' for i in range(n_samples)],
            'location': np.random.choice(locations, n_samples),
            'salary_min': np.random.randint(80000, 150000, n_samples),
            'salary_max': np.random.randint(120000, 250000, n_samples),
            'experience_level': np.random.choice(['Entry', 'Mid', 'Senior', 'Lead'], n_samples),
            'posted_date': pd.date_range('2023-01-01', periods=n_samples, freq='H')[:n_samples],
            'skills': np.random.choice([
                'Python, SQL, ML', 'Python, R, Statistics', 'SQL, Tableau, Python',
                'TensorFlow, Python, AWS', 'R, Shiny, Statistics'
            ], n_samples)
        }
        
        self.df = pd.DataFrame(data)
        # Add derived columns
        self.df['salary_avg'] = (self.df['salary_min'] + self.df['salary_max']) / 2
        self.df['posted_month'] = self.df['posted_date'].dt.month
        self.df['posted_weekday'] = self.df['posted_date'].dt.day_name()
        
        print(f"Created sample dataset with {len(self.df)} records")
        return self.df
    
    def clean_location_data(self):
        """Clean and standardize location data"""
        if self.df is None:
            return
        
        # Extract city and state
        self.df['city'] = self.df['location'].apply(
            lambda x: x.split(',')[0].strip() if ',' in str(x) else x
        )
        self.df['state'] = self.df['location'].apply(
            lambda x: x.split(',')[-1].strip() if ',' in str(x) else 'Unknown'
        )
        
        # Standardize major cities
        major_cities = {
            'SF': 'San Francisco', 'NYC': 'New York', 'LA': 'Los Angeles',
            'DC': 'Washington', 'Remote US': 'Remote'
        }
        
        for abbrev, full_name in major_cities.items():
            self.df['city'] = self.df['city'].replace(abbrev, full_name)
    
    def analyze_demand_supply(self):
        """Analyze demand vs supply by location"""
        if self.df is None:
            return None
        
        # Group by location to get demand counts
        demand_by_location = self.df.groupby('city').size().sort_values(ascending=False)
        
        # For supply, we'll simulate based on population/tech hub data
        # In real scenario, you'd get this from talent databases
        supply_factors = {
            'San Francisco': 1.0, 'New York': 0.9, 'Seattle': 0.8, 'Austin': 0.6,
            'Boston': 0.7, 'Denver': 0.5, 'Chicago': 0.7, 'Washington': 0.6,
            'Los Angeles': 0.6, 'Remote': 1.2
        }
        
        # Create supply simulation (higher in tech hubs)
        supply_data = []
        for city, demand in demand_by_location.items():
            factor = supply_factors.get(city, 0.5)  # Default factor
            supply = int(demand * factor * np.random.uniform(0.8, 1.2))
            supply_data.append({
                'city': city,
                'demand': demand,
                'supply': supply,
                'demand_supply_ratio': demand / max(supply, 1)
            })
        
        return pd.DataFrame(supply_data).sort_values('demand_supply_ratio', ascending=False)
    
    def plot_demand_vs_supply(self):
        """Create demand vs supply visualization"""
        demand_supply_df = self.analyze_demand_supply()
        if demand_supply_df is None:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Bar chart comparison
        x_pos = range(len(demand_supply_df))
        width = 0.35
        
        ax1.bar([x - width/2 for x in x_pos], demand_supply_df['demand'], 
                width, label='Demand', alpha=0.8)
        ax1.bar([x + width/2 for x in x_pos], demand_supply_df['supply'], 
                width, label='Supply', alpha=0.8)
        
        ax1.set_xlabel('Cities')
        ax1.set_ylabel('Number of Positions')
        ax1.set_title('Job Demand vs Talent Supply by Location')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(demand_supply_df['city'], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Ratio analysis
        colors = ['red' if ratio > 1.5 else 'orange' if ratio > 1 else 'green' 
                 for ratio in demand_supply_df['demand_supply_ratio']]
        
        bars = ax2.bar(range(len(demand_supply_df)), demand_supply_df['demand_supply_ratio'], 
                      color=colors, alpha=0.7)
        ax2.set_xlabel('Cities')
        ax2.set_ylabel('Demand/Supply Ratio')
        ax2.set_title('Market Competition Index\n(Red = High Competition, Green = Low Competition)')
        ax2.set_xticks(range(len(demand_supply_df)))
        ax2.set_xticklabels(demand_supply_df['city'], rotation=45, ha='right')
        ax2.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Balanced Market')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return demand_supply_df
    
    def analyze_salary_trends(self):
        """Analyze salary trends by various factors"""
        if self.df is None:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Salary by experience level
        sns.boxplot(data=self.df, x='experience_level', y='salary_avg', ax=axes[0,0])
        axes[0,0].set_title('Salary Distribution by Experience Level')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Salary by location (top 10 cities)
        top_cities = self.df.groupby('city')['salary_avg'].mean().nlargest(10)
        axes[0,1].bar(range(len(top_cities)), top_cities.values)
        axes[0,1].set_xlabel('Cities')
        axes[0,1].set_ylabel('Average Salary ($)')
        axes[0,1].set_title('Top 10 Highest Paying Cities')
        axes[0,1].set_xticks(range(len(top_cities)))
        axes[0,1].set_xticklabels(top_cities.index, rotation=45, ha='right')
        
        # Salary vs Demand correlation
        city_stats = self.df.groupby('city').agg({
            'salary_avg': 'mean',
            'title': 'count'
        }).rename(columns={'title': 'job_count'})
        
        scatter = axes[1,0].scatter(city_stats['job_count'], city_stats['salary_avg'], 
                                  c=range(len(city_stats)), cmap='viridis', alpha=0.7)
        axes[1,0].set_xlabel('Number of Job Postings')
        axes[1,0].set_ylabel('Average Salary ($)')
        axes[1,0].set_title('Job Demand vs Average Salary\n(Each point = One City)')
        plt.colorbar(scatter, ax=axes[1,0])
        
        # Salary distribution histogram
        axes[1,1].hist(self.df['salary_avg'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        axes[1,1].set_xlabel('Average Salary ($)')
        axes[1,1].set_ylabel('Frequency')
        axes[1,1].set_title('Distribution of Data Scientist Salaries')
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Print key statistics
        print("\n=== SALARY ANALYSIS SUMMARY ===")
        print(f"Overall Average Salary: ${self.df['salary_avg'].mean():,.0f}")
        print(f"Salary Range: ${self.df['salary_avg'].min():,.0f} - ${self.df['salary_avg'].max():,.0f}")
        print("\nAverage Salary by Experience Level:")
        exp_salaries = self.df.groupby('experience_level')['salary_avg'].mean().sort_values(ascending=False)
        for level, salary in exp_salaries.items():
            print(f"  {level}: ${salary:,.0f}")
    
    def create_interactive_dashboard(self):
        """Create interactive Plotly dashboard"""
        if self.df is None:
            return
        
        # Prepare data for visualization
        city_stats = self.df.groupby('city').agg({
            'salary_avg': 'mean',
            'title': 'count'
        }).round(0).rename(columns={'title': 'job_count'})
        
        # Interactive scatter plot
        fig = px.scatter(
            city_stats.reset_index(),
            x='job_count',
            y='salary_avg',
            size='job_count',
            color='salary_avg',
            hover_name='city',
            title='Job Market Dashboard: Demand vs Salary by City',
            labels={
                'job_count': 'Number of Job Postings',
                'salary_avg': 'Average Salary ($)'
            },
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            xaxis_title="Number of Job Postings",
            yaxis_title="Average Salary ($)",
            hovermode='closest'
        )
        
        fig.show()
        
        # Interactive bar chart for experience levels
        exp_data = self.df.groupby(['experience_level', 'city']).size().reset_index(name='count')
        fig2 = px.bar(
            exp_data,
            x='experience_level',
            y='count',
            color='city',
            title='Job Distribution by Experience Level and City',
            barmode='group'
        )
        
        fig2.show()
    
    def generate_report(self):
        """Generate comprehensive market analysis report"""
        if self.df is None:
            return
        
        print("=" * 50)
        print("DATA SCIENTIST JOB MARKET ANALYSIS REPORT")
        print("=" * 50)
        
        print(f"\n📊 DATASET OVERVIEW")
        print(f"Total Job Listings: {len(self.df):,}")
        print(f"Date Range: {self.df['posted_date'].min()} to {self.df['posted_date'].max()}")
        
        print(f"\n📍 TOP LOCATIONS BY JOB COUNT")
        top_locations = self.df['location'].value_counts().head(10)
        for i, (location, count) in enumerate(top_locations.items(), 1):
            print(f"  {i}. {location}: {count:,} jobs")
        
        print(f"\n💼 SALARY INSIGHTS")
        avg_salary = self.df['salary_avg'].mean()
        print(f"Average Salary: ${avg_salary:,.0f}")
        print(f"Highest Salary Range: ${self.df['salary_max'].max():,}")
        print(f"Lowest Salary Range: ${self.df['salary_min'].min():,}")
        
        print(f"\n📈 EXPERIENCE LEVEL DISTRIBUTION")
        exp_dist = self.df['experience_level'].value_counts()
        for level, count in exp_dist.items():
            percentage = (count / len(self.df)) * 100
            print(f"  {level}: {count:,} ({percentage:.1f}%)")
        
        print(f"\n🏢 MOST IN DEMAND SKILLS")
        # This would require parsing skills column properly
        print("Skills analysis would be implemented based on job descriptions")
        
        print("=" * 50)

def main():
    """Main function to demonstrate the analyzer"""
    # Initialize analyzer
    analyzer = JobMarketAnalyzer()
    
    # Create sample data (in real scenario, load from CSV)
    analyzer.create_sample_data()
    analyzer.clean_location_data()
    
    # Generate visualizations
    print("Generating demand vs supply analysis...")
    analyzer.plot_demand_vs_supply()
    
    print("Analyzing salary trends...")
    analyzer.analyze_salary_trends()
    
    print("Creating interactive dashboard...")
    analyzer.create_interactive_dashboard()
    
    print("Generating comprehensive report...")
    analyzer.generate_report()

if __name__ == "__main__":
    main()