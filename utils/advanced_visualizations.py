import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')

class AdvancedJobVisualizer:
    def __init__(self, df):
        self.df = df.copy()
        
    def create_correlation_heatmap(self):
        """Create correlation heatmap for numerical variables"""
        # Select numerical columns
        numeric_cols = ['salary_min', 'salary_max', 'salary_avg']
        if 'posted_month' in self.df.columns:
            numeric_cols.append('posted_month')
            
        corr_matrix = self.df[numeric_cols].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5)
        plt.title('Correlation Matrix: Salary and Temporal Factors')
        plt.tight_layout()
        plt.show()
    
    def create_time_series_analysis(self):
        """Analyze job posting trends over time"""
        if 'posted_date' not in self.df.columns:
            return
            
        # Daily trend
        daily_posts = self.df.groupby(self.df['posted_date'].dt.date).size()
        
        # Monthly trend
        monthly_posts = self.df.groupby(self.df['posted_date'].dt.month).size()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Daily trend
        daily_posts.plot(ax=ax1, marker='o', linewidth=2, markersize=4)
        ax1.set_title('Daily Job Posting Trends')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Number of Job Postings')
        ax1.grid(True, alpha=0.3)
        
        # Monthly trend
        monthly_posts.plot(kind='bar', ax=ax2, color='skyblue', edgecolor='black')
        ax2.set_title('Monthly Job Posting Distribution')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Number of Job Postings')
        ax2.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def create_skill_wordcloud(self):
        """Create word cloud from job skills/descriptions"""
        if 'skills' not in self.df.columns:
            return
            
        # Combine all skills text
        text = ' '.join(self.df['skills'].astype(str))
        
        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, 
                            background_color='white',
                            max_words=100,
                            colormap='viridis').generate(text)
        
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Most Common Skills in Data Science Job Postings', fontsize=16)
        plt.show()
    
    def create_market_competition_index(self):
        """Create comprehensive market competition visualization"""
        # Calculate competition metrics
        city_metrics = self.df.groupby('city').agg({
            'salary_avg': ['mean', 'std'],
            'title': 'count'
        }).round(2)
        
        city_metrics.columns = ['avg_salary', 'salary_std', 'job_count']
        city_metrics['competition_index'] = (
            city_metrics['job_count'] / city_metrics['avg_salary'] * 1000
        )
        
        # Create comprehensive visualization
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Job Count by City', 'Average Salary by City',
                          'Competition Index', 'Salary vs Job Count'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Top cities by job count
        top_cities = city_metrics.nlargest(10, 'job_count')
        fig.add