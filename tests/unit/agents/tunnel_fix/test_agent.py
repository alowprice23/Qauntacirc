import unittest
from unittest.mock import Mock, patch
import numpy as np

from agents.tunnel_fix.agent import TunnelFixAgent
from core.types import SystemState, EnergyBreakdown, LyapunovMetrics, PerformanceBarrier, SoftwareState
from agents.base.contracts import Proposal
from monitoring.performance import PerformanceProfile, PerformanceBottleneck
from math_utils.optimization import OptimizationCandidate

class MockLLMClient:
    def __init__(self):
        pass

class TestTunnelFixAgent(unittest.TestCase):

    def setUp(self):
        self.llm_client = MockLLMClient()
        self.agent = TunnelFixAgent(llm_client=self.llm_client)
        self.state = SystemState(
            software_state=SoftwareState(),
            energy_breakdown=EnergyBreakdown(total=100, complexity=50, coupling=30, constraint=10, debt=10),
            lyapunov_metrics=LyapunovMetrics(phi=1.0, energy=100, test_penalty=0, obligation_penalty=0)
        )

    @patch('agents.tunnel_fix.agent.PerformanceProfiler')
    def test_guard_returns_true_on_bottlenecks(self, MockPerformanceProfiler):
        mock_profiler_instance = MockPerformanceProfiler.return_value
        mock_profiler_instance.profile_system.return_value = PerformanceProfile(
            timestamp=0,
            system_state_hash=0,
            profiles={},
            overall_score=50,
            bottlenecks=[
                PerformanceBottleneck(
                    type="cpu",
                    location="some_function",
                    severity=0.5,
                    description="High CPU usage",
                    optimization_candidates=[]
                )
            ]
        )
        self.agent.profiler = mock_profiler_instance
        self.assertTrue(self.agent.guard(self.state))

    @patch('agents.tunnel_fix.agent.PerformanceProfiler')
    def test_guard_returns_false_on_no_bottlenecks(self, MockPerformanceProfiler):
        mock_profiler_instance = MockPerformanceProfiler.return_value
        mock_profiler_instance.profile_system.return_value = PerformanceProfile(
            timestamp=0,
            system_state_hash=0,
            profiles={},
            overall_score=100,
            bottlenecks=[]
        )
        self.agent.profiler = mock_profiler_instance
        self.assertFalse(self.agent.guard(self.state))

    @patch('agents.tunnel_fix.agent.BarrierEscapeOptimizer')
    @patch('agents.tunnel_fix.agent.PerformanceProfiler')
    def test_propose_returns_valid_proposal(self, MockPerformanceProfiler, MockBarrierEscapeOptimizer):
        mock_profiler_instance = MockPerformanceProfiler.return_value
        mock_profiler_instance.profile_system.return_value = PerformanceProfile(
            timestamp=0,
            system_state_hash=0,
            profiles={},
            overall_score=50,
            bottlenecks=[
                PerformanceBottleneck(
                    type="cpu",
                    location="some_function",
                    severity=0.8,
                    description="High CPU usage",
                    optimization_candidates=[]
                )
            ]
        )
        self.agent.profiler = mock_profiler_instance

        mock_optimizer_instance = MockBarrierEscapeOptimizer.return_value
        mock_optimizer_instance.generate_optimization_candidates.return_value = [
            OptimizationCandidate(
                type="caching",
                changes="Implement caching",
                expected_speedup=2.0,
                complexity_increase=0.1
            )
        ]
        mock_optimizer_instance.estimate_performance_gain.return_value = 1.5
        self.agent.optimizer = mock_optimizer_instance

        # Mocking _identify_performance_barriers to return a predictable barrier
        self.agent._identify_performance_barriers = Mock(return_value=[
            PerformanceBarrier(id='cpu-some_function', height=0.8, width=0.15, location='some_function')
        ])

        proposal = self.agent.propose(self.state)

        self.assertIsInstance(proposal, Proposal)
        self.assertEqual(proposal.agent_id, "tunnel_fix")
        self.assertEqual(len(proposal.optimizations), 1)
        self.assertEqual(proposal.optimizations[0].optimization_type, "caching")
        self.assertGreater(proposal.optimizations[0].tunneling_probability, 0)

if __name__ == '__main__':
    unittest.main()
