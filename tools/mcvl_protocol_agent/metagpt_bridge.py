from __future__ import annotations
import json
from .models import AnalysisReport, PacketCapture

SYSTEM_CONTRACT = "You are MCVLProtocolAnalyst. Analyze only supplied evidence. Never invent packet semantics. Separate OBSERVED, HYPOTHESIS and REQUIRED_EVIDENCE. A hypothesis cannot be VERIFIED from one capture. Do not generate server handlers. Return JSON only."

def build_prompt(captures: list[PacketCapture], report: AnalysisReport) -> str:
    evidence=[{"capture_id":c.capture_id,"pid":c.pid,"direction":c.direction,"session":c.session,"raw_hex":c.raw_hex,"response_packets":c.response_packets} for c in captures]
    return SYSTEM_CONTRACT+"\n\nEVIDENCE:\n"+json.dumps(evidence,indent=2)+"\n\nDETERMINISTIC_REPORT:\n"+json.dumps(report.to_dict(),indent=2)

def normalize_agent_output(data: dict) -> dict:
    data.setdefault("observed",[]); data.setdefault("hypotheses",[]); data.setdefault("required_evidence",[])
    for h in data["hypotheses"]:
        h["status"]="hypothesis"; h["verified"]=False
    return data
