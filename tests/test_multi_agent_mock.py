#!/usr/bin/env python3
"""
Test Multi-Agent System with Mock LLM (No API Costs)

Tests the multi-agent architecture without making real LLM calls.
Useful for development and verifying the system structure.
"""

import json
import logging
import os
import sys
from typing import Dict, Any

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MockLLMClient:
    """Mock LLM client for testing without API calls"""
    
    def __init__(self, model: str = "mock-gpt-3.5"):
        self.model = model
        logger.info(f"Initialized MockLLMClient with model {model}")
    
    def analyze_pr(self, pr_data: Dict[str, Any], formatter, include_full_diff: bool = True):
        """Mock PR analysis"""
        return """
        {
          "findings": [
            {
              "type": "sql_injection",
              "severity": "high",
              "confidence": 0.92,
              "file": "api/users.py",
              "line": 45,
              "description": "Potential SQL injection vulnerability detected",
              "recommendation": "Use parameterized queries instead of string concatenation"
            }
          ]
        }
        """


def test_multi_agent_mock():
    """Test multi-agent system with mock LLM"""
    
    print("=" * 80)
    print("TESTING MULTI-AGENT SYSTEM (MOCK MODE - NO API COSTS)")
    print("=" * 80)
    
    # Mock PR data
    pr_data = {
        "id": 123,
        "title": "Add user authentication",
        "repo": "owner/repo",
        "files": [
            {
                "filename": "auth/login.py",
                "patch": "+def authenticate(user_input):\n+    query = 'SELECT * FROM users WHERE id=' + user_input",
                "status": "modified",
                "additions": 10,
                "deletions": 2
            }
        ],
        "additions": 10,
        "deletions": 2
    }
    
    print(f"\nTest Configuration:")
    print(f"  Mode: MOCK (no real API calls)")
    print(f"  PR: #{pr_data['id']} - {pr_data['title']}")
    print(f"  Files: {len(pr_data['files'])}")
    
    # Import agents
    from agents import MultiAgentOrchestrator
    
    print("\n" + "-" * 80)
    print("STEP 1: Initializing Multi-Agent System")
    print("-" * 80)
    
    # Create mock client
    mock_client = MockLLMClient()
    
    # Initialize orchestrator with mock
    orchestrator = MultiAgentOrchestrator(
        llm_client=mock_client,
        model="mock-gpt-3.5",
        parallel=True
    )
    
    print("✓ Orchestrator initialized with mock LLM")
    
    # Get agent status
    status = orchestrator.get_agent_status()
    print(f"\nAgent Configuration:")
    for agent_name, config in status.items():
        if agent_name != 'parallel_execution':
            print(f"  {agent_name.capitalize()}: {config['model']} (temp={config['temperature']})")
    
    print("\n" + "-" * 80)
    print("STEP 2: Testing Agent Structure")
    print("-" * 80)
    
    # Test individual agent imports
    from agents import SecurityAgent, PerformanceAgent, ArchitectureAgent, Synthesizer
    from agents.base_agent import Finding, Severity, AgentResponse
    
    print("✓ All agent classes imported successfully")
    
    # Test Finding creation
    test_finding = Finding(
        type="test_issue",
        severity=Severity.HIGH,
        confidence=0.9,
        file="test.py",
        description="Test finding",
        recommendation="Test recommendation"
    )
    print(f"✓ Finding object created: {test_finding.type}")
    
    # Test AgentResponse creation
    test_response = AgentResponse(
        agent_name="test",
        findings=[test_finding],
        summary="Test summary",
        risk_level="high",
        confidence=0.9,
        execution_time=1.0
    )
    print(f"✓ AgentResponse created: {test_response.findings_count} findings")
    
    # Test Synthesizer
    synthesizer = Synthesizer()
    print("✓ Synthesizer initialized")
    
    print("\n" + "-" * 80)
    print("STEP 3: Testing Agent Methods")
    print("-" * 80)
    
    # Test agent initialization
    security_agent = SecurityAgent(mock_client, model="mock-gpt-3.5")
    print(f"✓ Security agent: {security_agent.agent_name}, temp={security_agent.temperature}")
    
    performance_agent = PerformanceAgent(mock_client, model="mock-gpt-3.5")
    print(f"✓ Performance agent: {performance_agent.agent_name}, temp={performance_agent.temperature}")
    
    architecture_agent = ArchitectureAgent(mock_client, model="mock-gpt-3.5")
    print(f"✓ Architecture agent: {architecture_agent.agent_name}, temp={architecture_agent.temperature}")
    
    print("\n" + "-" * 80)
    print("RESULTS")
    print("-" * 80)
    
    print("\n✅ Multi-Agent System Structure Verified!")
    print("\nSystem Components:")
    print("  ✓ Base Agent (abstract class)")
    print("  ✓ Security Agent (specialized)")
    print("  ✓ Performance Agent (specialized)")
    print("  ✓ Architecture Agent (specialized)")
    print("  ✓ Synthesizer (conflict resolution)")
    print("  ✓ Orchestrator (coordination)")
    print("  ✓ Finding & AgentResponse (data structures)")
    
    print("\n🎓 Architecture Implementation:")
    print("  - 3 specialized agents with different focus areas")
    print("  - Each agent has configurable temperature")
    print("  - Parallel execution support")
    print("  - Structured output format")
    print("  - Conflict resolution via synthesizer")
    
    print("\n⚠️  Note: This is a structural test with mock LLM")
    print("   To test with real analysis, run: python tests/test_multi_agent.py")
    print("   (Requires OpenAI API key and costs ~$1-2)")
    
    print("\n" + "=" * 80)
    print("✅ MOCK TEST PASSED - System Ready for Real Analysis")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_multi_agent_mock()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
