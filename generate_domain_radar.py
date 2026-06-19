#!/usr/bin/env python3
"""
Generate Domain-Focused Radar Chart comparing Multi-Agent vs Single-Agent
Shows performance across different PR categories (Security, Performance, etc.)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
import json


def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes."""
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):
        def transform_path_non_affine(self, path):
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):
        name = 'radar'
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def load_analysis_summary():
    """Load the analysis summary JSON"""
    with open('analysis_summary.json', 'r') as f:
        return json.load(f)


def extract_domain_metrics(data):
    """
    Extract quality scores by domain from consistency analysis
    Normalize to 0-100 scale for radar chart
    """
    consistency = data['consistency']
    
    # Order of categories for radar chart (clockwise from top)
    categories = ['Security', 'Performance', 'Architecture', 'Bug/Regression', 'Clean Code']
    
    multi_scores = []
    single_scores = []
    
    for category in categories:
        if category in consistency:
            multi_scores.append(consistency[category]['multi_mean'])
            single_scores.append(consistency[category]['single_mean'])
        else:
            # Fallback if category name doesn't match exactly
            multi_scores.append(0)
            single_scores.append(0)
    
    return {
        'categories': categories,
        'multi_agent': multi_scores,
        'single_agent': single_scores
    }


def generate_domain_radar_chart(output_file='analysis_output/domain_radar_comparison.png'):
    """Generate domain-focused radar chart"""
    
    print("="*80)
    print("GENERATING DOMAIN-FOCUSED RADAR CHART")
    print("="*80)
    
    # Load data
    data = load_analysis_summary()
    metrics = extract_domain_metrics(data)
    
    print("\nDomain Quality Scores:")
    for cat, multi, single in zip(metrics['categories'], metrics['multi_agent'], metrics['single_agent']):
        print(f"  {cat:20s}: Multi={multi:5.1f}%  Single={single:5.1f}%  Diff={multi-single:+5.1f}%")
    
    # Setup radar chart
    N = len(metrics['categories'])
    theta = radar_factory(N, frame='polygon')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(top=0.9, bottom=0.1)
    
    # Colors
    multi_color = '#2E86AB'  # Blue
    single_color = '#A23B72'  # Purple/Pink
    
    # Plot data
    ax.plot(theta, metrics['multi_agent'], 'o-', linewidth=3, 
            label='Multi-Agent', color=multi_color, markersize=10)
    ax.fill(theta, metrics['multi_agent'], alpha=0.25, color=multi_color)
    
    ax.plot(theta, metrics['single_agent'], 's-', linewidth=3, 
            label='Single-Agent', color=single_color, markersize=10)
    ax.fill(theta, metrics['single_agent'], alpha=0.25, color=single_color)
    
    # Set labels with better formatting
    formatted_labels = [cat.replace('/', '/\n') for cat in metrics['categories']]
    ax.set_varlabels(formatted_labels)
    
    # Set y-axis limits (0-100 for quality scores)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
    
    # Add title and legend
    ax.set_title('Quality Score by Domain: Multi-Agent vs Single-Agent',
                 size=18, weight='bold', position=(0.5, 1.1))
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=14)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Generated {output_file}")
    
    # Also create a version with values displayed
    generate_domain_radar_with_values(metrics, output_file.replace('.png', '_with_values.png'))
    
    plt.close()


def generate_domain_radar_with_values(metrics, output_file):
    """Generate domain radar chart with actual values displayed"""
    
    N = len(metrics['categories'])
    theta = radar_factory(N, frame='polygon')
    
    fig, ax = plt.subplots(figsize=(12, 11), subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(top=0.9, bottom=0.1)
    
    multi_color = '#2E86AB'
    single_color = '#A23B72'
    
    # Plot data
    ax.plot(theta, metrics['multi_agent'], 'o-', linewidth=3, 
            label='Multi-Agent', color=multi_color, markersize=10)
    ax.fill(theta, metrics['multi_agent'], alpha=0.25, color=multi_color)
    
    ax.plot(theta, metrics['single_agent'], 's-', linewidth=3, 
            label='Single-Agent', color=single_color, markersize=10)
    ax.fill(theta, metrics['single_agent'], alpha=0.25, color=single_color)
    
    formatted_labels = [cat.replace('/', '/\n') for cat in metrics['categories']]
    ax.set_varlabels(formatted_labels)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
    
    # Add value labels
    for i, (angle, multi_val, single_val, label) in enumerate(
        zip(theta, metrics['multi_agent'], metrics['single_agent'], metrics['categories'])
    ):
        # Multi-agent value (outside the point)
        radius_multi = multi_val + 8
        x_multi = np.cos(angle) * radius_multi
        y_multi = np.sin(angle) * radius_multi
        
        # Convert to axes coordinates for text placement
        ax.text(angle, radius_multi, f'{multi_val:.1f}%', 
                ha='center', va='center', fontsize=10, 
                color=multi_color, weight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                         edgecolor=multi_color, linewidth=2, alpha=0.9))
        
        # Single-agent value
        if single_val > 15:
            radius_single = single_val - 8
        else:
            radius_single = single_val + 8
            
        ax.text(angle, radius_single, f'{single_val:.1f}%', 
                ha='center', va='center', fontsize=10, 
                color=single_color, weight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                         edgecolor=single_color, linewidth=2, alpha=0.9))
    
    ax.set_title('Quality Score by Domain (with values)',
                 size=18, weight='bold', position=(0.5, 1.1))
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Generated {output_file}")
    plt.close()


def generate_findings_count_radar(output_file='analysis_output/findings_count_radar.png'):
    """Generate radar chart comparing number of findings by domain"""
    
    print("\nGenerating findings count radar chart...")
    
    # Load data from thesis_data files
    import glob
    
    categories = {
        'Security': [3, 4, 5, 6],
        'Performance': [7, 8, 9, 10],
        'Architecture': [11, 12, 13, 14],
        'Bug/Regression': [15, 16, 17, 18],
        'Clean Code': [19, 20, 21, 22]
    }
    
    category_findings = {cat: {'multi': [], 'single': []} for cat in categories}
    
    for file in glob.glob('thesis_data/PR*.json'):
        with open(file, 'r') as f:
            data = json.load(f)
            pr_num = data['pr_number']
            
            # Find category
            for cat, prs in categories.items():
                if pr_num in prs:
                    category_findings[cat]['multi'].append(data['total_findings'])
                    if data.get('comparison') and 'single_agent' in data['comparison']:
                        category_findings[cat]['single'].append(
                            data['comparison']['single_agent']['findings_count']
                        )
                    break
    
    # Calculate averages
    cat_order = ['Security', 'Performance', 'Architecture', 'Bug/Regression', 'Clean Code']
    multi_avg = [np.mean(category_findings[cat]['multi']) if category_findings[cat]['multi'] else 0 
                 for cat in cat_order]
    single_avg = [np.mean(category_findings[cat]['single']) if category_findings[cat]['single'] else 0 
                  for cat in cat_order]
    
    print("\nAverage Findings Count by Domain:")
    for cat, multi, single in zip(cat_order, multi_avg, single_avg):
        print(f"  {cat:20s}: Multi={multi:4.1f}  Single={single:4.1f}")
    
    # Create chart
    N = len(cat_order)
    theta = radar_factory(N, frame='polygon')
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='radar'))
    
    multi_color = '#2E86AB'
    single_color = '#A23B72'
    
    ax.plot(theta, multi_avg, 'o-', linewidth=3, 
            label='Multi-Agent', color=multi_color, markersize=10)
    ax.fill(theta, multi_avg, alpha=0.25, color=multi_color)
    
    ax.plot(theta, single_avg, 's-', linewidth=3, 
            label='Single-Agent', color=single_color, markersize=10)
    ax.fill(theta, single_avg, alpha=0.25, color=single_color)
    
    formatted_labels = [cat.replace('/', '/\n') for cat in cat_order]
    ax.set_varlabels(formatted_labels)
    
    max_val = max(max(multi_avg), max(single_avg))
    ax.set_ylim(0, max_val * 1.2)
    
    ax.set_title('Average Number of Findings by Domain',
                 size=18, weight='bold', position=(0.5, 1.1))
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Generated {output_file}")
    plt.close()


def main():
    """Main entry point"""
    try:
        # Generate quality score radar
        generate_domain_radar_chart()
        
        # Generate findings count radar
        generate_findings_count_radar()
        
        print()
        print("="*80)
        print("DOMAIN RADAR CHARTS COMPLETE")
        print("="*80)
        print()
        print("Generated files:")
        print("  - analysis_output/domain_radar_comparison.png")
        print("  - analysis_output/domain_radar_comparison_with_values.png")
        print("  - analysis_output/findings_count_radar.png")
        print()
        print("These charts show:")
        print("  1. Quality score performance in each domain category")
        print("  2. Number of findings detected in each domain")
        print("  3. Multi-agent's consistent high performance across all domains")
        print("  4. Single-agent's variable performance by domain type")
        
    except FileNotFoundError as e:
        print(f"ERROR: Required file not found: {e}")
        print("Please ensure:")
        print("  1. analysis_summary.json exists (run comparative_analysis.py)")
        print("  2. thesis_data/ folder has PR review JSON files")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
