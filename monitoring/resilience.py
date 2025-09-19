import asyncio
import time
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from pydantic import BaseModel

# Assuming these data classes are in core.chaos_types
try:
    from core.chaos_types import ChaosScenario, ResilienceReport
except ImportError:
    # Fallback for local testing
    from typing import Callable
    from pydantic import BaseModel

    class ChaosScenario(BaseModel):
        name: str
        description: str
        target_components: List[str]
        fault_injection: Callable
        expected_behavior: str
        recovery_criteria: Dict[str, Any]
        blast_radius: float
        duration_seconds: int
        class Config:
            arbitrary_types_allowed = True

    class ResilienceReport(BaseModel):
        scenario_name: str
        baseline_metrics: Dict[str, Any]
        chaos_metrics: Dict[str, Any]
        recovery_metrics: Dict[str, Any]
        resilience_score: float
        recovery_time: float
        sla_violations: int
        data_consistency_maintained: bool
        recommendations: List[str]
        class Config:
            arbitrary_types_allowed = True


class ResilienceAnalysisResult(BaseModel):
    """Data class to hold the results of resilience analysis."""
    score: float
    sla_violations: int
    data_consistency: bool
    recommendations: List[str]


class ResilienceMonitor:
    """Monitors system resilience during chaos testing."""

    def __init__(self):
        self.metrics_collectors: Dict[str, Any] = {}
        self.baseline_metrics: Dict[str, Any] = {}
        self.alert_thresholds: Dict[str, Any] = {}

    async def _collect_metrics(self, components: List[str], duration: int) -> Dict[str, Any]:
        """Generic metric collection placeholder."""
        print(f"Collecting metrics for {components} over {duration} seconds...")
        await asyncio.sleep(duration / 10)  # Simulate metric collection time
        return {
            "latency_ms": random.uniform(50, 150),
            "error_rate": random.uniform(0, 0.05),
            "throughput_rpm": random.uniform(1000, 5000),
        }

    async def _collect_baseline_metrics(self, components: List[str], duration: int) -> Dict[str, Any]:
        """Collect baseline performance and health metrics."""
        return await self._collect_metrics(components, duration)

    async def _collect_chaos_metrics(self, components: List[str], duration: int) -> Dict[str, Any]:
        """Collect metrics during the chaos injection."""
        # Simulate degraded performance
        metrics = await self._collect_metrics(components, duration)
        metrics["latency_ms"] *= random.uniform(2, 5)
        metrics["error_rate"] *= random.uniform(10, 20)
        return metrics

    async def _collect_recovery_metrics(self, components: List[str], duration: int) -> Dict[str, Any]:
        """Collect metrics during the recovery phase."""
        return await self._collect_metrics(components, duration)

    def _analyze_resilience(
        self,
        baseline: Dict[str, Any],
        chaos: Dict[str, Any],
        recovery: Dict[str, Any],
        scenario: ChaosScenario,
    ) -> ResilienceAnalysisResult:
        """Analyze the collected metrics to assess resilience."""
        # Simple scoring logic: compare recovery to baseline
        latency_impact = (chaos["latency_ms"] - baseline["latency_ms"]) / baseline["latency_ms"]
        error_impact = (chaos["error_rate"] - baseline["error_rate"])

        recovery_score = 1.0
        if recovery["latency_ms"] > baseline["latency_ms"] * 1.2:
            recovery_score -= 0.3
        if recovery["error_rate"] > baseline["error_rate"] * 1.5:
            recovery_score -= 0.3

        # Overall resilience score
        score = (1.0 - latency_impact * 0.2 - error_impact * 10) * recovery_score
        score = max(0.0, min(1.0, score)) # Clamp between 0 and 1

        recommendations = []
        if score < 0.6:
            recommendations.append("System did not recover within acceptable limits. Review recovery procedures.")
        if scenario.recovery_criteria.get("data_consistency") and random.random() < 0.1:
             recommendations.append("Data consistency check failed. Investigate potential data loss.")


        return ResilienceAnalysisResult(
            score=score,
            sla_violations=int(error_impact * 1000), # Heuristic
            data_consistency=random.choice([True, False]), # Placeholder
            recommendations=recommendations,
        )

    async def monitor_chaos_scenario(
        self, scenario: ChaosScenario, baseline_duration: int = 60
    ) -> ResilienceReport:
        """Monitor system behavior during a chaos scenario execution."""
        print(f"--- Starting Chaos Scenario: {scenario.name} ---")

        # 1. Collect baseline metrics
        print("Step 1: Collecting baseline metrics...")
        baseline_metrics = await self._collect_baseline_metrics(
            scenario.target_components, baseline_duration
        )
        self.baseline_metrics = baseline_metrics
        print(f"Baseline metrics: {baseline_metrics}")

        # 2. Execute chaos scenario
        print("Step 2: Injecting fault...")
        chaos_start_time = time.time()
        injection_result = await scenario.fault_injection(
            scenario.target_components, scenario.duration_seconds
        )
        print(f"Fault injection result: {injection_result}")

        # 3. Monitor system behavior during chaos
        print("Step 3: Monitoring during chaos...")
        chaos_metrics = await self._collect_chaos_metrics(
            scenario.target_components, scenario.duration_seconds
        )
        print(f"Chaos metrics: {chaos_metrics}")

        # 4. Monitor recovery phase
        print("Step 4: Monitoring recovery...")
        recovery_start_time = time.time()
        max_recovery_time = scenario.recovery_criteria.get("max_recovery_time", 300)
        recovery_metrics = await self._collect_recovery_metrics(
            scenario.target_components, max_recovery_time
        )
        recovery_end_time = time.time()
        print(f"Recovery metrics: {recovery_metrics}")

        # 5. Analyze resilience
        print("Step 5: Analyzing resilience...")
        resilience_analysis = self._analyze_resilience(
            baseline_metrics, chaos_metrics, recovery_metrics, scenario
        )

        report = ResilienceReport(
            scenario_name=scenario.name,
            baseline_metrics=baseline_metrics,
            chaos_metrics=chaos_metrics,
            recovery_metrics=recovery_metrics,
            resilience_score=resilience_analysis.score,
            recovery_time=recovery_end_time - recovery_start_time,
            sla_violations=resilience_analysis.sla_violations,
            data_consistency_maintained=resilience_analysis.data_consistency,
            recommendations=resilience_analysis.recommendations,
        )
        print(f"--- Chaos Scenario Finished: {scenario.name} ---")
        print(f"Resilience Score: {report.resilience_score:.2f}")
        return report
