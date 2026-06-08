# Advanced Scoring System Guide

## Overview

The advanced scoring system provides sophisticated, configurable prioritization of findings from multiple agents. Instead of simple priority-based ranking, it considers multiple weighted factors to calculate comprehensive scores.

## Formula

```
final_score = (
    severity_score * severity_weight +
    agent_score * agent_weight +
    confidence * confidence_weight +
    impact_score * impact_weight +
    complexity_score * complexity_weight +
    criticality_score * criticality_weight +
    urgency_score * urgency_weight
) * severity_multiplier * agent_multiplier
```

## Factors

### Core Scoring Factors

1. **Severity Score** (0.0-1.0)
   - CRITICAL: 1.0
   - HIGH: 0.75
   - MEDIUM: 0.5
   - LOW: 0.25
   - INFO: 0.1

2. **Agent Score** (0.0-1.0)
   - Security: 1.0
   - Performance: 0.8
   - Architecture: 0.6

3. **Confidence** (0.0-1.0)
   - Direct from finding

4. **Impact Score** (0.0-1.0)
   - Composite of:
     - Technical Impact (30%): How much code affected
     - Business Impact (50%): User/revenue consequence
     - Maintenance Impact (20%): Future burden

5. **Complexity Score** (0.0-1.0)
   - Estimated from description keywords
   - High complexity = harder to fix

6. **Criticality Score** (0.0-1.0)
   - Based on file patterns:
     - auth, security, payment → 0.9
     - service, controller → 0.6
     - test, util → 0.3

7. **Urgency Score** (0.0-1.0)
   - Based on severity + impact
   - Boosted for security issues

### Weights (Default Balanced)

```python
severity_weight = 10.0
agent_weight = 5.0
confidence_weight = 3.0
impact_weight = 7.0
complexity_weight = 2.0
criticality_weight = 4.0
urgency_weight = 3.0
```

### Multipliers

```python
# Agent multipliers
agent_multipliers = {
    'security': 1.0,
    'performance': 1.0,
    'architecture': 1.0
}

# Severity multipliers
severity_multipliers = {
    'critical': 1.0,
    'high': 1.0,
    'medium': 1.0,
    'low': 1.0,
    'info': 1.0
}
```

## Presets

### 1. Balanced (Default)

Equal consideration of all factors.

```python
orchestrator = MultiAgentOrchestrator(
    llm_client,
    use_advanced_scoring=True,
    scoring_preset='balanced'
)
```

### 2. Security Critical

For banking, healthcare, authentication systems.

**Key adjustments:**
- Security findings: 2.5x multiplier
- Severity weight: 12.0 (high)
- Impact weight: 10.0 (critical)
- Urgency weight: 5.0 (urgent)
- Critical severity: 1.5x multiplier
- Performance/Architecture: 0.7x/0.6x

```python
orchestrator = MultiAgentOrchestrator(
    llm_client,
    use_advanced_scoring=True,
    scoring_preset='security_critical'
)
```

**Use when:**
- Handling sensitive data (PII, financial, health)
- Authentication/authorization systems
- Payment processing
- Regulatory compliance required

### 3. Performance Critical

For high-traffic APIs, real-time systems.

**Key adjustments:**
- Performance findings: 2.5x multiplier
- Impact weight: 10.0 (performance impact critical)
- Complexity weight: 4.0 (complexity affects performance)
- Security/Architecture: 0.8x/1.0x

```python
orchestrator = MultiAgentOrchestrator(
    llm_client,
    use_advanced_scoring=True,
    scoring_preset='performance_critical'
)
```

**Use when:**
- High-traffic APIs
- Real-time systems
- Gaming servers
- Latency-sensitive applications

### 4. Architecture Focused

For large codebases, long-term projects.

**Key adjustments:**
- Architecture findings: 2.0x multiplier
- Complexity weight: 5.0 (very important)
- Urgency weight: 2.0 (less time pressure)
- Focus on maintainability

```python
orchestrator = MultiAgentOrchestrator(
    llm_client,
    use_advanced_scoring=True,
    scoring_preset='architecture_focused'
)
```

**Use when:**
- Large, established codebases
- Long-term maintenance projects
- Technical debt cleanup
- Refactoring initiatives

### 5. Startup MVP

For rapid development, ship fast.

**Key adjustments:**
- Severity weight: 12.0 (fix critical bugs)
- Urgency weight: 6.0 (ship fast)
- Architecture: 0.5x multiplier (can wait)
- Critical severity: 2.0x multiplier (must fix)
- Low/Info: 0.3x/0.1x (ignore for MVP)

```python
orchestrator = MultiAgentOrchestrator(
    llm_client,
    use_advanced_scoring=True,
    scoring_preset='startup_mvp'
)
```

**Use when:**
- Building MVPs/prototypes
- Early-stage startups
- Speed to market critical
- Can iterate on architecture later

## Custom Weight Profiles

Create your own weight profile:

```python
from agents import WeightProfile, MultiAgentOrchestrator

custom_weights = WeightProfile(
    severity_weight=15.0,      # Very important
    agent_weight=3.0,          # Less important
    confidence_weight=5.0,     # Trust high confidence
    impact_weight=12.0,        # Critical factor
    complexity_weight=2.0,
    criticality_weight=8.0,
    urgency_weight=6.0,
    
    # Agent-specific boosts
    agent_multipliers={
        'security': 1.8,
        'performance': 1.5,
        'architecture': 0.8
    },
    
    # Severity-specific boosts
    severity_multipliers={
        'critical': 2.0,       # 2x for critical
        'high': 1.5,
        'medium': 1.0,
        'low': 0.5,
        'info': 0.2
    }
)

orchestrator = MultiAgentOrchestrator(
    llm_client,
    use_advanced_scoring=True,
    weight_profile=custom_weights
)
```

## Comparison: Simple vs Advanced

### Simple Scoring (Default)

```python
# Priority = (severity, agent_priority, confidence)
sorted_findings = sorted(findings, 
    key=lambda f: (severity_score, agent_priority, confidence),
    reverse=True
)
```

**Pros:**
- Fast and simple
- Predictable
- Easy to understand

**Cons:**
- No impact consideration
- No file criticality
- Fixed agent priorities
- No context awareness

### Advanced Scoring

```python
score = sum of all weighted factors * multipliers
```

**Pros:**
- Considers 7+ factors
- Customizable per project
- Context-aware (impact, criticality)
- Fine-grained control

**Cons:**
- More complex
- Requires configuration
- Harder to debug

## When to Use Each

### Use Simple Scoring When:
- Quick analysis needed
- Project type doesn't matter
- Default priorities work well
- Simplicity preferred

### Use Advanced Scoring When:
- Project has specific priorities (e.g., security-critical)
- Need to consider business impact
- Want fine-grained control
- Comparing different prioritization strategies
- Conducting research/evaluation

## Output Differences

### Simple Scoring Output

```json
{
  "priority": 1,
  "severity": "high",
  "agent": "security",
  "type": "sql_injection",
  "confidence": 0.92
}
```

### Advanced Scoring Output

```json
{
  "priority": 1,
  "severity": "high",
  "agent": "security",
  "type": "sql_injection",
  "confidence": 0.92,
  "score": 42.5,
  "normalized_score": 85.0,
  "score_breakdown": {
    "severity_score": 7.5,
    "agent_score": 5.0,
    "confidence_score": 2.76,
    "impact_score": 6.3,
    "complexity_score": 1.6,
    "criticality_score": 3.6,
    "urgency_score": 2.7
  },
  "score_factors": {
    "severity": "high",
    "agent": "security",
    "confidence": 0.92,
    "impact": 0.9,
    "complexity": 0.8,
    "criticality": 0.9,
    "urgency": 0.9
  }
}
```

## Best Practices

1. **Start with presets**: Use built-in presets before creating custom profiles

2. **Test both methods**: Run analysis with simple and advanced scoring to compare

3. **Document your choice**: Note which preset/weights you used for reproducibility

4. **Adjust iteratively**: Start with a preset, then fine-tune based on results

5. **Consider your domain**: 
   - Financial/Healthcare → `security_critical`
   - High-traffic API → `performance_critical`
   - Legacy codebase → `architecture_focused`
   - New startup → `startup_mvp`

6. **Validate results**: Check if top priorities make sense for your project

## Examples

See `example_advanced_scoring.py` for complete examples of:
- Using all presets
- Creating custom profiles
- Comparing simple vs advanced scoring
- Analyzing real PRs with different configurations

## Integration with Evaluation

For thesis evaluation, you can:

1. **Compare scoring methods**:
   ```python
   # Run same PR with different methods
   report_simple = orchestrator_simple.analyze_pr(pr_data)
   report_advanced = orchestrator_advanced.analyze_pr(pr_data)
   ```

2. **Evaluate different contexts**:
   ```python
   # Same PR, different weight profiles
   for preset in ['balanced', 'security_critical', 'performance_critical']:
       orchestrator = MultiAgentOrchestrator(
           llm_client,
           use_advanced_scoring=True,
           scoring_preset=preset
       )
       report = orchestrator.analyze_pr(pr_data)
       # Compare top priorities
   ```

3. **Measure impact of weights**:
   ```python
   # Vary weights systematically
   for severity_w in [5.0, 10.0, 15.0]:
       profile = WeightProfile(severity_weight=severity_w, ...)
       # Analyze and record results
   ```

## Future Enhancements

Potential improvements:
- Machine learning to learn optimal weights
- Historical data to estimate impact more accurately
- Project-specific configuration files
- A/B testing framework for weight optimization
- Integration with CI/CD metrics

## References

- `agents/scoring.py`: Implementation
- `agents/synthesizer.py`: Integration with synthesizer
- `agents/orchestrator.py`: Orchestrator configuration
- `example_advanced_scoring.py`: Usage examples
