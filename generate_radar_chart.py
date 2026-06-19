#!/usr/bin/env python3
"""
Generate Radar Chart comparing Multi-Agent vs Single-Agent
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
    """
    Create a radar chart with `num_vars` axes.
    
    This function creates a RadarAxes projection and registers it.
    """
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


def normalize_metrics(data):
    """
    Normalize metrics to 0-1 scale for radar chart
    
    Returns dict with normalized values for both systems
    """
    quality = data['quality_scores']
    specificity = data['specificity']
    consistency = data['consistency']
    timing = data['execution_time']
    
    # Calculate normalized metrics (0-1 scale, higher is better)
    
    # Quality Score (already 0-100, divide by 100)
    multi_quality = quality['multi_mean'] / 100
    single_quality = quality['single_mean'] / 100
    
    # Consistency (inverse of std dev, normalized)
    # Lower std dev is better, so inverse and normalize
    max_std = max(quality['multi_std'], quality['single_std'])
    multi_consistency = 1 - (quality['multi_std'] / max_std)
    single_consistency = 1 - (quality['single_std'] / max_std)
    
    # Specificity (already 0-1)
    multi_specificity = specificity['multi_agent']
    single_specificity = specificity['single_agent']
    
    # Speed (inverse of time, normalized)
    # Faster is better, so inverse and normalize
    max_time = max(timing['multi_avg'], timing['single_avg'])
    multi_speed = 1 - (timing['multi_avg'] / max_time)
    single_speed = 1 - (timing['single_avg'] / max_time)
    
    # Calculate average specialization from consistency data
    # Higher category focus = better specialization
    multi_specializations = []
    single_specializations = []
    
    for cat, metrics in consistency.items():
        # Use inverse of std dev as proxy for specialization
        # More consistent = more specialized
        multi_specializations.append(1 / (metrics['multi_std'] + 1))
        single_specializations.append(1 / (metrics['single_std'] + 1))
    
    multi_specialization = np.mean(multi_specializations)
    single_specialization = np.mean(single_specializations)
    
    # Normalize specialization to 0-1
    max_spec = max(multi_specialization, single_specialization)
    multi_specialization = multi_specialization / max_spec
    single_specialization = single_specialization / max_spec
    
    # Focus (inverse of findings count - fewer, more focused findings)
    # Multi-agent: 4.5 findings, Single-agent: 12.3 findings
    # Lower is better (more focused), so inverse
    multi_findings = 4.5
    single_findings = 12.3
    max_findings = max(multi_findings, single_findings)
    multi_focus = 1 - (multi_findings / max_findings)
    single_focus = 1 - (single_findings / max_findings)
    
    return {
        'multi_agent': [
            multi_quality,
            multi_consistency,
            multi_specificity,
            multi_speed,
            multi_specialization,
            multi_focus
        ],
        'single_agent': [
            single_quality,
            single_consistency,
            single_specificity,
            single_speed,
            single_specialization,
            single_focus
        ],
        'labels': [
            'Quality Score',
            'Consistency',
            'Specificity',
            'Speed',
            'Specialization',
            'Focus'
        ]
    }


def generate_radar_chart(output_file='analysis_output/radar_comparison.png'):
    """Generate radar chart comparing multi-agent vs single-agent"""
    
    print("="*80)
    print("GENERATING RADAR CHART COMPARISON")
    print("="*80)
    
    # Load data
    data = load_analysis_summary()
    metrics = normalize_metrics(data)
    
    # Setup radar chart
    N = len(metrics['labels'])
    theta = radar_factory(N, frame='polygon')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(top=0.9, bottom=0.1)
    
    # Colors
    multi_color = '#2E86AB'  # Blue
    single_color = '#A23B72'  # Purple/Pink
    
    # Plot data
    ax.plot(theta, metrics['multi_agent'], 'o-', linewidth=2.5, 
            label='Multi-Agent', color=multi_color, markersize=8)
    ax.fill(theta, metrics['multi_agent'], alpha=0.25, color=multi_color)
    
    ax.plot(theta, metrics['single_agent'], 's-', linewidth=2.5, 
            label='Single-Agent', color=single_color, markersize=8)
    ax.fill(theta, metrics['single_agent'], alpha=0.25, color=single_color)
    
    # Set labels
    ax.set_varlabels(metrics['labels'])
    
    # Set y-axis limits
    ax.set_ylim(0, 1)
    
    # Add title and legend
    ax.set_title('Multi-Agent vs Single-Agent: Performance Comparison',
                 size=16, weight='bold', position=(0.5, 1.1))
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Generated {output_file}")
    
    # Also create a version with metric values displayed
    generate_radar_with_values(metrics, output_file.replace('.png', '_with_values.png'))
    
    plt.close()


def generate_radar_with_values(metrics, output_file):
    """Generate radar chart with actual metric values displayed"""
    
    N = len(metrics['labels'])
    theta = radar_factory(N, frame='polygon')
    
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(top=0.9, bottom=0.1)
    
    multi_color = '#2E86AB'
    single_color = '#A23B72'
    
    # Plot data
    ax.plot(theta, metrics['multi_agent'], 'o-', linewidth=2.5, 
            label='Multi-Agent', color=multi_color, markersize=8)
    ax.fill(theta, metrics['multi_agent'], alpha=0.25, color=multi_color)
    
    ax.plot(theta, metrics['single_agent'], 's-', linewidth=2.5, 
            label='Single-Agent', color=single_color, markersize=8)
    ax.fill(theta, metrics['single_agent'], alpha=0.25, color=single_color)
    
    ax.set_varlabels(metrics['labels'])
    ax.set_ylim(0, 1)
    
    # Add value labels
    for i, (angle, multi_val, single_val, label) in enumerate(
        zip(theta, metrics['multi_agent'], metrics['single_agent'], metrics['labels'])
    ):
        # Position for multi-agent value
        x_multi = angle
        y_multi = multi_val + 0.08
        ax.text(x_multi, y_multi, f'{multi_val:.2f}', 
                ha='center', va='center', fontsize=9, 
                color=multi_color, weight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Position for single-agent value
        x_single = angle
        y_single = single_val - 0.08 if single_val > 0.15 else single_val + 0.08
        ax.text(x_single, y_single, f'{single_val:.2f}', 
                ha='center', va='center', fontsize=9, 
                color=single_color, weight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.set_title('Multi-Agent vs Single-Agent: Detailed Performance Metrics',
                 size=16, weight='bold', position=(0.5, 1.1))
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Generated {output_file}")
    plt.close()


def main():
    """Main entry point"""
    try:
        generate_radar_chart()
        
        print()
        print("="*80)
        print("RADAR CHART GENERATION COMPLETE")
        print("="*80)
        print()
        print("Generated files:")
        print("  - analysis_output/radar_comparison.png")
        print("  - analysis_output/radar_comparison_with_values.png")
        print()
        print("Metrics compared:")
        print("  1. Quality Score - Overall code review quality (0-100%)")
        print("  2. Consistency - Low variance across PRs (higher = more reliable)")
        print("  3. Specificity - Actionable findings with file/line details")
        print("  4. Speed - Execution time (faster = better)")
        print("  5. Specialization - Domain expertise in specific areas")
        print("  6. Focus - Fewer, higher-quality findings vs many generic ones")
        
    except FileNotFoundError:
        print("ERROR: analysis_summary.json not found")
        print("Please run: python comparative_analysis.py")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
