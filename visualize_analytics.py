#!/usr/bin/env python3
"""
Analytics Visualization Module
Generates charts and graphs for test analytics
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Set style for better-looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AnalyticsVisualizer:
    def __init__(self, analytics_file="test_analytics.json"):
        self.analytics_file = analytics_file
        self.output_dir = "charts"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_analytics(self):
        """Load analytics data from JSON file"""
        try:
            with open(self.analytics_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Analytics file {self.analytics_file} not found!")
            return None
    
    def create_current_test_charts(self, test_results):
        """Create charts for the current test run"""
        print("Generating current test run charts...")
        
        # Extract metrics from test results
        metrics = {
            'True Positives': test_results['true_positives'],
            'True Negatives': test_results['true_negatives'],
            'False Positives': test_results['false_positives'],
            'False Negatives': test_results['false_negatives']
        }
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Current Test Run Analytics', fontsize=16, fontweight='bold')
        
        # 1. Confusion Matrix Heatmap
        confusion_matrix = np.array([
            [metrics['True Negatives'], metrics['False Positives']],
            [metrics['False Negatives'], metrics['True Positives']]
        ])
        
        sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Predicted Safe', 'Predicted Harmful'],
                   yticklabels=['Actual Safe', 'Actual Harmful'], ax=ax1)
        ax1.set_title('Confusion Matrix')
        
        # 2. Metrics Bar Chart
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
        bars = ax2.bar(metrics.keys(), metrics.values(), color=colors)
        ax2.set_title('Performance Metrics')
        ax2.set_ylabel('Count')
        
        # Add value labels on bars
        for bar, value in zip(bars, metrics.values()):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(value), ha='center', va='bottom', fontweight='bold')
        
        # 3. Pie Chart - Success vs Failure
        total = sum(metrics.values())
        success = metrics['True Positives'] + metrics['True Negatives']
        failure = metrics['False Positives'] + metrics['False Negatives']
        
        ax3.pie([success, failure], labels=['Success', 'Failure'], 
               autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'])
        ax3.set_title('Success vs Failure Rate')
        
        # 4. Precision, Recall, F1-Score
        precision = metrics['True Positives'] / (metrics['True Positives'] + metrics['False Positives']) if (metrics['True Positives'] + metrics['False Positives']) > 0 else 0
        recall = metrics['True Positives'] / (metrics['True Positives'] + metrics['False Negatives']) if (metrics['True Positives'] + metrics['False Negatives']) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        scores = [precision, recall, f1_score]
        score_labels = ['Precision', 'Recall', 'F1-Score']
        
        bars = ax4.bar(score_labels, scores, color=['#9b59b6', '#e67e22', '#1abc9c'])
        ax4.set_title('Precision, Recall, and F1-Score')
        ax4.set_ylabel('Score')
        ax4.set_ylim(0, 1)
        
        # Add value labels
        for bar, score in zip(bars, scores):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/current_test_analytics.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Save metrics summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'total_tests': total,
            'success_rate': (success / total) * 100 if total > 0 else 0
        }
        
        with open(f'{self.output_dir}/current_test_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Current test charts saved to {self.output_dir}/")
        return summary
    
    def create_overall_analytics_charts(self):
        """Create charts for overall analytics from JSON file"""
        print("Generating overall analytics charts...")
        
        data = self.load_analytics()
        if not data:
            return
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Overall Analytics Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Query Volume Over Time
        if 'session_data' in data and data['session_data']:
            df = pd.DataFrame(data['session_data'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
            daily_counts = df.groupby('date').size()
            ax1.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=6)
            ax1.set_title('Daily Query Volume')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Number of Queries')
            ax1.tick_params(axis='x', rotation=45)
        
        # 2. Category Distribution
        if 'categories_blocked' in data:
            categories = list(data['categories_blocked'].keys())
            counts = list(data['categories_blocked'].values())
            
            # Sort by count for better visualization
            sorted_data = sorted(zip(categories, counts), key=lambda x: x[1], reverse=True)
            categories, counts = zip(*sorted_data)
            
            bars = ax2.barh(categories, counts, color=sns.color_palette("husl", len(categories)))
            ax2.set_title('Queries by Category')
            ax2.set_xlabel('Count')
            
            # Add value labels
            for i, (bar, count) in enumerate(zip(bars, counts)):
                ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                        str(count), ha='left', va='center', fontweight='bold')
        
        # 3. Risk Level Distribution
        if 'risk_levels' in data:
            risk_levels = list(data['risk_levels'].keys())
            risk_counts = list(data['risk_levels'].values())
            
            colors = ['#2ecc71', '#f39c12', '#e74c3c']  # Green, Orange, Red
            wedges, texts, autotexts = ax3.pie(risk_counts, labels=risk_levels, autopct='%1.1f%%', colors=colors)
            ax3.set_title('Risk Level Distribution')
        
        # 4. Performance Metrics Over Time
        if 'session_data' in data and data['session_data']:
            df = pd.DataFrame(data['session_data'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
            # Calculate daily performance metrics
            daily_metrics = df.groupby('date').agg({
                'blocked': ['sum', 'count']
            }).reset_index()
            daily_metrics.columns = ['date', 'blocked_count', 'total_count']
            daily_metrics['block_rate'] = (daily_metrics['blocked_count'] / daily_metrics['total_count']) * 100
            
            ax4.plot(daily_metrics['date'], daily_metrics['block_rate'], 
                    marker='s', linewidth=2, markersize=6, color='#e74c3c')
            ax4.set_title('Daily Block Rate (%)')
            ax4.set_xlabel('Date')
            ax4.set_ylabel('Block Rate (%)')
            ax4.tick_params(axis='x', rotation=45)
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/overall_analytics.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Create additional detailed charts
        self.create_detailed_charts(data)
        
        print(f"Overall analytics charts saved to {self.output_dir}/")
    
    def create_detailed_charts(self, data):
        """Create additional detailed charts"""
        
        # 1. Hourly Activity Pattern
        if 'session_data' in data and data['session_data']:
            df = pd.DataFrame(data['session_data'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
            hourly_counts = df.groupby('hour').size()
            
            plt.figure(figsize=(12, 6))
            plt.plot(hourly_counts.index, hourly_counts.values, marker='o', linewidth=2, markersize=8)
            plt.title('Hourly Activity Pattern', fontsize=14, fontweight='bold')
            plt.xlabel('Hour of Day')
            plt.ylabel('Number of Queries')
            plt.grid(True, alpha=0.3)
            plt.xticks(range(0, 24))
            plt.savefig(f'{self.output_dir}/hourly_activity.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # 2. Block Rate by Category
        if 'categories_blocked' in data and 'session_data' in data:
            df = pd.DataFrame(data['session_data'])
            category_block_rates = df.groupby('category').agg({
                'blocked': ['sum', 'count']
            })
            category_block_rates.columns = ['blocked_count', 'total_count']
            category_block_rates['block_rate'] = (category_block_rates['blocked_count'] / category_block_rates['total_count']) * 100
            
            plt.figure(figsize=(12, 8))
            bars = plt.barh(category_block_rates.index, category_block_rates['block_rate'], 
                           color=sns.color_palette("viridis", len(category_block_rates)))
            plt.title('Block Rate by Category', fontsize=14, fontweight='bold')
            plt.xlabel('Block Rate (%)')
            plt.ylabel('Category')
            
            # Add value labels
            for i, (bar, rate) in enumerate(zip(bars, category_block_rates['block_rate'])):
                plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                        f'{rate:.1f}%', ha='left', va='center', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/category_block_rates.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    def generate_report(self, test_results=None):
        """Generate a comprehensive analytics report"""
        print("Generating comprehensive analytics report...")
        
        # Create current test charts if results provided
        if test_results:
            current_summary = self.create_current_test_charts(test_results)
        
        # Create overall analytics charts
        self.create_overall_analytics_charts()
        
        # Generate text report
        self.generate_text_report(test_results)
        
        print(f"All charts and reports saved to {self.output_dir}/")
    
    def generate_text_report(self, test_results=None):
        """Generate a text-based analytics report"""
        data = self.load_analytics()
        if not data:
            return
        
        report = []
        report.append("=" * 60)
        report.append("ANALYTICS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall Statistics
        report.append("OVERALL STATISTICS")
        report.append("-" * 30)
        report.append(f"Total Queries: {data.get('total_queries', 0)}")
        report.append(f"Blocked Queries: {data.get('blocked_queries', 0)}")
        report.append(f"Block Rate: {(data.get('blocked_queries', 0) / max(data.get('total_queries', 1), 1) * 100):.2f}%")
        report.append("")
        
        # Performance Metrics
        if test_results:
            report.append("CURRENT TEST PERFORMANCE")
            report.append("-" * 30)
            report.append(f"True Positives: {test_results['true_positives']}")
            report.append(f"True Negatives: {test_results['true_negatives']}")
            report.append(f"False Positives: {test_results['false_positives']}")
            report.append(f"False Negatives: {test_results['false_negatives']}")
            
            total = sum(test_results.values())
            success_rate = ((test_results['true_positives'] + test_results['true_negatives']) / total) * 100
            report.append(f"Success Rate: {success_rate:.2f}%")
            report.append("")
        
        # Category Analysis
        if 'categories_blocked' in data:
            report.append("CATEGORY ANALYSIS")
            report.append("-" * 30)
            for category, count in sorted(data['categories_blocked'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"{category}: {count} queries")
            report.append("")
        
        # Risk Level Analysis
        if 'risk_levels' in data:
            report.append("RISK LEVEL ANALYSIS")
            report.append("-" * 30)
            for level, count in data['risk_levels'].items():
                percentage = (count / max(data.get('total_queries', 1), 1)) * 100
                report.append(f"{level.capitalize()}: {count} queries ({percentage:.1f}%)")
        
        # Save report
        with open(f'{self.output_dir}/analytics_report.txt', 'w') as f:
            f.write('\n'.join(report))
        
        # Print report
        print('\n'.join(report))

def main():
    """Main function for standalone usage"""
    visualizer = AnalyticsVisualizer()
    
    # Example test results (replace with actual results)
    test_results = {
        'true_positives': 16,
        'true_negatives': 13,
        'false_positives': 0,
        'false_negatives': 2
    }
    
    visualizer.generate_report(test_results)

if __name__ == "__main__":
    main() 