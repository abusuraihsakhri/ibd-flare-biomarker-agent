"""
Enrichment Feature Implementation for ibd-flare-biomarker-agent.
Generated based on domain-specific requirements in specifications.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import datetime

# =============================================================================
# BASE RESULT & ENGINE (shared by all enrichment modules)
# =============================================================================
@dataclass
class EnrichmentResult:
    """Shared result type for every enrichment engine."""
    feature_name: str = "Enrichment"
    status: str = "OPTIMAL"
    score: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class BaseEnrichmentEngine:
    """
    Shared evaluation logic for every enrichment domain engine.

    Each subclass — or dynamically built instance — supplies only a
    ``feature_name`` and optional ``threshold`` / ``config``.
    """
    def __init__(self, feature_name: str, threshold: float = 1.0,
                 config: Optional[Dict[str, Any]] = None):
        self.feature_name = feature_name
        self.threshold = threshold
        self.config = config or {}
        self.history: List[EnrichmentResult] = []

    def evaluate(self, primary_value: float, secondary_value: float = 0.0,
                 **kwargs) -> EnrichmentResult:
        alerts: List[str] = []
        recs: List[str] = []
        status = "OPTIMAL"
        score = round(float(primary_value), 3)

        if primary_value > self.threshold * 2:
            status = "CRITICAL_ALERT"
            alerts.append(
                f"{self.feature_name}: Primary value {primary_value:.2f} "
                f"breached critical threshold ({self.threshold * 2:.2f})"
            )
            recs.append("Initiate immediate protocol review and escalate to attending lead.")
        elif primary_value > self.threshold:
            status = "WARNING"
            alerts.append(
                f"{self.feature_name}: Value {primary_value:.2f} exceeds "
                f"baseline threshold ({self.threshold:.2f})"
            )
            recs.append("Increase monitoring frequency and perform secondary verification.")
        else:
            recs.append("Parameters nominal under standard operating bounds.")

        res = EnrichmentResult(
            feature_name=self.feature_name,
            status=status,
            score=score,
            metrics={"primary": primary_value, "secondary": secondary_value, **kwargs},
            alerts=alerts,
            recommendations=recs,
        )
        self.history.append(res)
        return res


# =============================================================================
# CONVENIENCE SUBCLASSES (preserve original public names for backward compat)
# =============================================================================
class FeaturesEngine(BaseEnrichmentEngine):
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Features", threshold, config)

class EndoscopyQualityMetricsDashboardEngine(BaseEnrichmentEngine):
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Endoscopy Quality Metrics Dashboard", threshold, config)

class IbdActivityScoringEngine(BaseEnrichmentEngine):
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("IBD Activity Scoring", threshold, config)

class LiverFibrosisAssessmentEngine(BaseEnrichmentEngine):
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Liver Fibrosis Assessment", threshold, config)

class GerdManagementProtocolEngine(BaseEnrichmentEngine):
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("GERD Management Protocol", threshold, config)

class PancreaticCystSurveillanceEngine(BaseEnrichmentEngine):
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Pancreatic Cyst Surveillance", threshold, config)

class CeliacDiseaseMonitoringEngine(BaseEnrichmentEngine):
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Celiac Disease Monitoring", threshold, config)

class ColorectalCancerScreeningEngine(BaseEnrichmentEngine):
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Colorectal Cancer Screening", threshold, config)

# =============================================================================
# COMPOSITE ENRICHMENT SUITE
# =============================================================================
class IbdflarebiomarkeragentEnrichmentSuite:
    """Master coordinator executing all enriched domain features."""
    def __init__(self):
        self.featuresengine = FeaturesEngine()
        self.endoscopyqualitymetr = EndoscopyQualityMetricsDashboardEngine()
        self.ibdactivityscoringen = IbdActivityScoringEngine()
        self.liverfibrosisassessm = LiverFibrosisAssessmentEngine()
        self.gerdmanagementprotoc = GerdManagementProtocolEngine()
        self.pancreaticcystsurvei = PancreaticCystSurveillanceEngine()
        self.celiacdiseasemonitor = CeliacDiseaseMonitoringEngine()
        self.colorectalcancerscre = ColorectalCancerScreeningEngine()

    def execute_all(self, primary_val: float = 1.5, secondary_val: float = 0.5) -> Dict[str, Any]:
        results = {}
        results["FeaturesEngine"] = self.featuresengine.evaluate(primary_val, secondary_val)
        results["EndoscopyQualityMetricsDashboardEngine"] = self.endoscopyqualitymetr.evaluate(primary_val, secondary_val)
        results["IbdActivityScoringEngine"] = self.ibdactivityscoringen.evaluate(primary_val, secondary_val)
        results["LiverFibrosisAssessmentEngine"] = self.liverfibrosisassessm.evaluate(primary_val, secondary_val)
        results["GerdManagementProtocolEngine"] = self.gerdmanagementprotoc.evaluate(primary_val, secondary_val)
        results["PancreaticCystSurveillanceEngine"] = self.pancreaticcystsurvei.evaluate(primary_val, secondary_val)
        results["CeliacDiseaseMonitoringEngine"] = self.celiacdiseasemonitor.evaluate(primary_val, secondary_val)
        results["ColorectalCancerScreeningEngine"] = self.colorectalcancerscre.evaluate(primary_val, secondary_val)
        return results

# =============================================================================
# BACKWARD-COMPATIBLE RESULT TYPE ALIASES
# Kept so that existing imports (e.g. tests) continue to resolve.
# =============================================================================
FeaturesEngineResult = EnrichmentResult
EndoscopyQualityMetricsDashboardEngineResult = EnrichmentResult
IbdActivityScoringEngineResult = EnrichmentResult
LiverFibrosisAssessmentEngineResult = EnrichmentResult
GerdManagementProtocolEngineResult = EnrichmentResult
PancreaticCystSurveillanceEngineResult = EnrichmentResult
CeliacDiseaseMonitoringEngineResult = EnrichmentResult
ColorectalCancerScreeningEngineResult = EnrichmentResult

# Global instance
enrichment_suite = IbdflarebiomarkeragentEnrichmentSuite()
