#!/usr/bin/env python3
"""
Comparative Analysis: Multi-Agent vs Single-Agent PR Review
Without Ground Truth

Analyzes results from data-collection-v2 branch and generates:
- Comparative metrics
- Statistical analysis
- Visualizations
- LaTeX tables for thesis
"""

import json
import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import pandas as pd

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class ComparativeAnalyzer:
    """Analyze multi-agent vs single-agent without ground truth"""
    
    def __init__(self, data_dir: str = "thesis_data"):
        self.data_dir = Path(data_dir)
        self.results = []
        self.pr_categories = {
            'Security': [3, 4, 5, 6],
            'Performance': [7, 8, 9, 10],
            'Architecture': [11, 12, 13, 14],
            'Bug/Regression': [15, 16, 17, 18],
            'Clean Code': [19, 20, 21, 22]
        }
        
    def load_data(self):
        """Load all review results from data directory"""
        print("Loading review results...")
        
        json_files = sorted(self.data_dir.glob("PR*.json"))
        
        for file in json_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    self.results.append(data)
            except Exception as e:
                print(f"Warning: Could not load {file}: {e}")
        
        print(f"✓ Loaded {len(self.results)} PR reviews")
        return len(self.results)
    
    def consensus_analysis(self) -> Dict:
        """Analyze agreement between multi-agent and single-agent"""
        print("\n" + "="*80)
        print("CONSENSUS ANALYSIS")
        print("="*80)
        
        consensus_data = []
        
        for result in self.results:
            if not result.get('comparison_mode'):
                continue
            
            pr_num = result['pr_number']
            
            # Get findings from both
            multi_findings = set()
            if 'all_findings' in result:
                for f in result['all_findings']:
                    key = (f.get('type', ''), f.get('file', ''), f.get('severity', ''))
                    multi_findings.add(key)
            
            single_findings = set()
            if 'comparison' in result and 'single_agent' in result['comparison']:
                for f in result['comparison']['single_agent'].get('findings', []):
                    key = (f.get('type', ''), f.get('file', ''), f.get('severity', ''))
                    single_findings.add(key)
            
            # Calculate overlap
            consensus = multi_findings & single_findings
            only_multi = multi_findings - single_findings
            only_single = single_findings - multi_findings
            total_unique = len(multi_findings | single_findings)
            
            if total_unique > 0:
                consensus_rate = len(consensus) / total_unique
            else:
                consensus_rate = 1.0  # Both found nothing
            
            consensus_data.append({
                'pr': pr_num,
                'consensus': len(consensus),
                'only_multi': len(only_multi),
                'only_single': len(only_single),
                'consensus_rate': consensus_rate
            })
            
            print(f"PR #{pr_num}:")
            print(f"  Both found: {len(consensus)}")
            print(f"  Only Multi: {len(only_multi)}")
            print(f"  Only Single: {len(only_single)}")
            print(f"  Consensus Rate: {consensus_rate:.2%}")
        
        if consensus_data:
            avg_consensus = np.mean([d['consensus_rate'] for d in consensus_data])
            print(f"\n📊 Average Consensus Rate: {avg_consensus:.2%}")
        
        return {
            'per_pr': consensus_data,
            'avg_consensus_rate': avg_consensus if consensus_data else 0
        }
    
    def specificity_analysis(self) -> Dict:
        """Measure specificity and actionability of findings"""
        print("\n" + "="*80)
        print("SPECIFICITY ANALYSIS")
        print("="*80)
        
        def score_finding(finding: Dict) -> float:
            """Score finding quality 0-1"""
            score = 0
            total = 5
            
            if finding.get('file'): score += 1
            if finding.get('line'): score += 1
            if finding.get('code_snippet'): score += 1
            if len(finding.get('recommendation', '')) > 50: score += 1
            if finding.get('severity') in ['critical', 'high']: score += 1
            
            return score / total
        
        multi_scores = []
        single_scores = []
        
        for result in self.results:
            # Multi-agent findings
            if 'all_findings' in result:
                for f in result['all_findings']:
                    multi_scores.append(score_finding(f))
            
            # Single-agent findings
            if result.get('comparison') and 'single_agent' in result['comparison']:
                for f in result['comparison']['single_agent'].get('findings', []):
                    single_scores.append(score_finding(f))
        
        avg_multi = np.mean(multi_scores) if multi_scores else 0
        avg_single = np.mean(single_scores) if single_scores else 0
        
        print(f"Multi-Agent Avg Specificity: {avg_multi:.3f}")
        print(f"Single-Agent Avg Specificity: {avg_single:.3f}")
        print(f"Difference: {(avg_multi - avg_single):.3f}")
        
        return {
            'multi_agent': avg_multi,
            'single_agent': avg_single,
            'difference': avg_multi - avg_single
        }
    
    def consistency_analysis(self) -> Dict:
        """Measure consistency within PR categories"""
        print("\n" + "="*80)
        print("CONSISTENCY ANALYSIS")
        print("="*80)
        
        category_scores = defaultdict(lambda: {'multi': [], 'single': []})
        
        for result in self.results:
            pr_num = result['pr_number']
            
            # Find category
            category = None
            for cat, prs in self.pr_categories.items():
                if pr_num in prs:
                    category = cat
                    break
            
            if category:
                category_scores[category]['multi'].append(result['quality_score'])
                
                if result.get('comparison') and 'single_agent' in result['comparison']:
                    single_score = result['comparison']['single_agent']['quality_score']
                    category_scores[category]['single'].append(single_score)
        
        consistency_results = {}
        
        for category, scores in category_scores.items():
            multi_std = np.std(scores['multi']) if len(scores['multi']) > 1 else 0
            single_std = np.std(scores['single']) if len(scores['single']) > 1 else 0
            
            print(f"\n{category}:")
            print(f"  Multi-Agent Std Dev: {multi_std:.2f}")
            print(f"  Single-Agent Std Dev: {single_std:.2f}")
            print(f"  Multi-Agent Mean: {np.mean(scores['multi']):.1f}")
            print(f"  Single-Agent Mean: {np.mean(scores['single']) if scores['single'] else 0:.1f}")
            
            consistency_results[category] = {
                'multi_std': multi_std,
                'single_std': single_std,
                'multi_mean': np.mean(scores['multi']),
                'single_mean': np.mean(scores['single']) if scores['single'] else 0
            }
        
        return consistency_results
    
    def specialization_analysis(self) -> Dict:
        """Check if multi-agent shows domain specialization"""
        print("\n" + "="*80)
        print("SPECIALIZATION ANALYSIS")
        print("="*80)
        
        specialization = {}
        
        for category, pr_list in self.pr_categories.items():
            category_results = [r for r in self.results if r['pr_number'] in pr_list]
            
            multi_findings_in_category = 0
            multi_total_findings = 0
            single_findings_in_category = 0
            single_total_findings = 0
            
            for result in category_results:
                # Multi-agent
                if 'agent_summaries' in result:
                    for agent_name, summary in result['agent_summaries'].items():
                        # Handle both dict and string formats
                        if isinstance(summary, dict):
                            issues = summary.get('issues_found', 0)
                        else:
                            # Try to extract number from string
                            import re
                            match = re.search(r'(\d+)\s+issues?', str(summary), re.IGNORECASE)
                            issues = int(match.group(1)) if match else 0
                        
                        multi_total_findings += issues
                        
                        # Check if agent matches category
                        if category.lower() in agent_name.lower():
                            multi_findings_in_category += issues
                
                # Single-agent
                if result.get('comparison') and 'single_agent' in result['comparison']:
                    single_total = result['comparison']['single_agent'].get('findings_count', 0)
                    single_total_findings += single_total
                    # Single agent doesn't have specialization - all findings are "general"
            
            multi_relevance = multi_findings_in_category / multi_total_findings if multi_total_findings > 0 else 0
            
            print(f"\n{category} PRs:")
            print(f"  Multi-Agent relevant findings: {multi_findings_in_category}/{multi_total_findings} ({multi_relevance:.1%})")
            print(f"  Single-Agent total findings: {single_total_findings}")
            
            specialization[category] = {
                'multi_relevance': multi_relevance,
                'multi_category_findings': multi_findings_in_category,
                'multi_total': multi_total_findings,
                'single_total': single_total_findings
            }
        
        return specialization
    
    def quality_score_comparison(self) -> Dict:
        """Compare quality scores between systems"""
        print("\n" + "="*80)
        print("QUALITY SCORE COMPARISON")
        print("="*80)
        
        multi_scores = []
        single_scores = []
        pr_numbers = []
        
        for result in self.results:
            pr_numbers.append(result['pr_number'])
            multi_scores.append(result['quality_score'])
            
            if result.get('comparison') and 'single_agent' in result['comparison']:
                single_scores.append(result['comparison']['single_agent']['quality_score'])
            else:
                single_scores.append(None)
        
        # Filter pairs where both exist
        valid_pairs = [(m, s) for m, s in zip(multi_scores, single_scores) if s is not None]
        
        if valid_pairs:
            multi_valid = [p[0] for p in valid_pairs]
            single_valid = [p[1] for p in valid_pairs]
            
            print(f"Multi-Agent Mean: {np.mean(multi_valid):.1f}%")
            print(f"Single-Agent Mean: {np.mean(single_valid):.1f}%")
            print(f"Multi-Agent Median: {np.median(multi_valid):.1f}%")
            print(f"Single-Agent Median: {np.median(single_valid):.1f}%")
            print(f"Multi-Agent Std: {np.std(multi_valid):.1f}")
            print(f"Single-Agent Std: {np.std(single_valid):.1f}")
            
            # Correlation
            correlation = np.corrcoef(multi_valid, single_valid)[0, 1]
            print(f"\nCorrelation: {correlation:.3f}")
            
            return {
                'multi_mean': np.mean(multi_valid),
                'single_mean': np.mean(single_valid),
                'multi_median': np.median(multi_valid),
                'single_median': np.median(single_valid),
                'multi_std': np.std(multi_valid),
                'single_std': np.std(single_valid),
                'correlation': correlation,
                'pr_scores': list(zip(pr_numbers, multi_scores, single_scores))
            }
        
        return {}
    
    def execution_time_comparison(self) -> Dict:
        """Compare execution times and efficiency"""
        print("\n" + "="*80)
        print("EXECUTION TIME COMPARISON")
        print("="*80)
        
        multi_times = []
        single_times = []
        
        for result in self.results:
            multi_times.append(result['execution_time'])
            
            if result.get('comparison') and 'single_agent' in result['comparison']:
                single_times.append(result['comparison']['single_agent']['execution_time'])
        
        if multi_times and single_times:
            avg_multi = np.mean(multi_times)
            avg_single = np.mean(single_times)
            overhead = (avg_multi - avg_single) / avg_single * 100
            
            print(f"Multi-Agent Avg Time: {avg_multi:.1f}s")
            print(f"Single-Agent Avg Time: {avg_single:.1f}s")
            print(f"Time Overhead: {overhead:.1f}%")
            
            return {
                'multi_avg': avg_multi,
                'single_avg': avg_single,
                'overhead_pct': overhead
            }
        
        return {}
    
    def generate_visualizations(self, output_dir: str = "analysis_output"):
        """Generate all comparison plots"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("\n" + "="*80)
        print("GENERATING VISUALIZATIONS")
        print("="*80)
        
        # 1. Quality Score Comparison
        self._plot_quality_scores(output_path)
        
        # 2. Category Performance
        self._plot_category_performance(output_path)
        
        # 3. Findings Distribution
        self._plot_findings_distribution(output_path)
        
        # 4. Execution Time
        self._plot_execution_time(output_path)
        
        print(f"\n✓ Visualizations saved to {output_path}/")
    
    def _plot_quality_scores(self, output_path: Path):
        """Plot quality score comparison"""
        multi_scores = [r['quality_score'] for r in self.results]
        single_scores = []
        pr_numbers = [r['pr_number'] for r in self.results]
        
        for r in self.results:
            if r.get('comparison') and 'single_agent' in r['comparison']:
                single_scores.append(r['comparison']['single_agent']['quality_score'])
            else:
                single_scores.append(None)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Line plot
        ax1.plot(pr_numbers, multi_scores, 'o-', label='Multi-Agent', linewidth=2)
        if any(s is not None for s in single_scores):
            valid_single = [(pr, s) for pr, s in zip(pr_numbers, single_scores) if s is not None]
            if valid_single:
                prs, scores = zip(*valid_single)
                ax1.plot(prs, scores, 's-', label='Single-Agent', linewidth=2)
        
        ax1.set_xlabel('PR Number')
        ax1.set_ylabel('Quality Score (%)')
        ax1.set_title('Quality Score Comparison Across PRs')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot
        valid_pairs = [(m, s) for m, s in zip(multi_scores, single_scores) if s is not None]
        if valid_pairs:
            multi_valid = [p[0] for p in valid_pairs]
            single_valid = [p[1] for p in valid_pairs]
            
            ax2.boxplot([multi_valid, single_valid])
            ax2.set_xticklabels(['Multi-Agent', 'Single-Agent'])
            ax2.set_ylabel('Quality Score (%)')
            ax2.set_title('Quality Score Distribution')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / 'quality_scores_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated quality_scores_comparison.png")
    
    def _plot_category_performance(self, output_path: Path):
        """Plot performance by PR category"""
        category_data = defaultdict(lambda: {'multi': [], 'single': []})
        
        for result in self.results:
            pr_num = result['pr_number']
            for cat, prs in self.pr_categories.items():
                if pr_num in prs:
                    category_data[cat]['multi'].append(result['quality_score'])
                    if result.get('comparison') and 'single_agent' in result['comparison']:
                        category_data[cat]['single'].append(
                            result['comparison']['single_agent']['quality_score']
                        )
        
        categories = list(category_data.keys())
        multi_means = [np.mean(category_data[cat]['multi']) for cat in categories]
        single_means = [np.mean(category_data[cat]['single']) if category_data[cat]['single'] else 0 
                       for cat in categories]
        
        x = np.arange(len(categories))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width/2, multi_means, width, label='Multi-Agent', alpha=0.8)
        ax.bar(x + width/2, single_means, width, label='Single-Agent', alpha=0.8)
        
        ax.set_xlabel('PR Category')
        ax.set_ylabel('Average Quality Score (%)')
        ax.set_title('Average Quality Score by PR Category')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_path / 'category_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated category_performance.png")
    
    def _plot_findings_distribution(self, output_path: Path):
        """Plot findings count distribution"""
        multi_findings = [r['total_findings'] for r in self.results]
        single_findings = []
        
        for r in self.results:
            if r.get('comparison') and 'single_agent' in r['comparison']:
                single_findings.append(r['comparison']['single_agent']['findings_count'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if single_findings:
            ax.scatter(multi_findings[:len(single_findings)], single_findings, alpha=0.6, s=100)
            ax.plot([0, max(max(multi_findings), max(single_findings))], 
                   [0, max(max(multi_findings), max(single_findings))], 
                   'r--', alpha=0.5, label='Equal findings')
            
            ax.set_xlabel('Multi-Agent Findings Count')
            ax.set_ylabel('Single-Agent Findings Count')
            ax.set_title('Findings Count Comparison')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path / 'findings_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✓ Generated findings_distribution.png")
    
    def _plot_execution_time(self, output_path: Path):
        """Plot execution time comparison"""
        multi_times = [r['execution_time'] for r in self.results]
        single_times = []
        pr_numbers = [r['pr_number'] for r in self.results]
        
        for r in self.results:
            if r.get('comparison') and 'single_agent' in r['comparison']:
                single_times.append(r['comparison']['single_agent']['execution_time'])
        
        if single_times:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x = np.arange(len(multi_times[:len(single_times)]))
            width = 0.35
            
            ax.bar(x - width/2, multi_times[:len(single_times)], width, 
                  label='Multi-Agent', alpha=0.8)
            ax.bar(x + width/2, single_times, width, 
                  label='Single-Agent', alpha=0.8)
            
            ax.set_xlabel('PR Number')
            ax.set_ylabel('Execution Time (seconds)')
            ax.set_title('Execution Time Comparison')
            ax.set_xticks(x)
            ax.set_xticklabels(pr_numbers[:len(single_times)])
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plt.savefig(output_path / 'execution_time.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✓ Generated execution_time.png")
    
    def generate_latex_table(self, output_file: str = "comparison_table.tex"):
        """Generate LaTeX table for thesis"""
        print("\n" + "="*80)
        print("GENERATING LATEX TABLE")
        print("="*80)
        
        # Collect summary statistics
        multi_scores = [r['quality_score'] for r in self.results]
        multi_findings = [r['total_findings'] for r in self.results]
        multi_times = [r['execution_time'] for r in self.results]
        
        single_scores = []
        single_findings = []
        single_times = []
        
        for r in self.results:
            if r.get('comparison') and 'single_agent' in r['comparison']:
                single_scores.append(r['comparison']['single_agent']['quality_score'])
                single_findings.append(r['comparison']['single_agent']['findings_count'])
                single_times.append(r['comparison']['single_agent']['execution_time'])
        
        latex = r"""\begin{table}[h]
\centering
\caption{Multi-Agent vs Single-Agent Comparison}
\label{tab:comparison}
\begin{tabular}{lcc}
\toprule
\textbf{Metric} & \textbf{Multi-Agent} & \textbf{Single-Agent} \\
\midrule
"""
        
        if single_scores:
            latex += f"Quality Score (mean) & {np.mean(multi_scores[:len(single_scores)]):.1f}\\% & {np.mean(single_scores):.1f}\\% \\\\\n"
            latex += f"Quality Score (median) & {np.median(multi_scores[:len(single_scores)]):.1f}\\% & {np.median(single_scores):.1f}\\% \\\\\n"
            latex += f"Quality Score (std) & {np.std(multi_scores[:len(single_scores)]):.1f} & {np.std(single_scores):.1f} \\\\\n"
            latex += f"Findings per PR (mean) & {np.mean(multi_findings[:len(single_findings)]):.1f} & {np.mean(single_findings):.1f} \\\\\n"
            latex += f"Execution Time (mean) & {np.mean(multi_times[:len(single_times)]):.1f}s & {np.mean(single_times):.1f}s \\\\\n"
            
            overhead = (np.mean(multi_times[:len(single_times)]) - np.mean(single_times)) / np.mean(single_times) * 100
            latex += f"Time Overhead & {overhead:.1f}\\% & --- \\\\\n"
        
        latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
        
        with open(output_file, 'w') as f:
            f.write(latex)
        
        print(f"✓ Generated {output_file}")
    
    def run_full_analysis(self):
        """Run complete comparative analysis"""
        print("="*80)
        print("COMPARATIVE ANALYSIS: MULTI-AGENT VS SINGLE-AGENT")
        print("="*80)
        
        if self.load_data() == 0:
            print("\n❌ No data found. Please ensure PR reviews are in thesis_data/")
            return
        
        # Run all analyses
        consensus = self.consensus_analysis()
        specificity = self.specificity_analysis()
        consistency = self.consistency_analysis()
        specialization = self.specialization_analysis()
        quality = self.quality_score_comparison()
        timing = self.execution_time_comparison()
        
        # Generate outputs
        self.generate_visualizations()
        self.generate_latex_table()
        
        # Save summary
        summary = {
            'consensus': consensus,
            'specificity': specificity,
            'consistency': consistency,
            'specialization': specialization,
            'quality_scores': quality,
            'execution_time': timing
        }
        
        with open('analysis_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print("\nGenerated files:")
        print("  - analysis_output/ (visualizations)")
        print("  - comparison_table.tex (for thesis)")
        print("  - analysis_summary.json (raw data)")


def main():
    analyzer = ComparativeAnalyzer(data_dir="thesis_data")
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
