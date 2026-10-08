from .models import AnalysisReport, FieldHypothesis, PacketCapture
MAGIC = bytes.fromhex("44344BFF")

def analyze_frame(capture: PacketCapture) -> AnalysisReport:
    raw = capture.raw
    report = AnalysisReport(capture_id=capture.capture_id,pid=capture.pid,frame_length=len(raw))
    if raw.startswith(MAGIC):
        report.header_candidates.append(FieldHypothesis("magic_candidate",0,4,raw[:4].hex(),1.0,"observed",["frame starts with 44 34 4B FF"]))
        report.known.append("bytes[0:4] == 44 34 4B FF")
    else:
        report.unknown.append("frame magic/prefix")
    if len(raw) >= 8:
        report.fields.append(FieldHypothesis("u32_be_candidate",4,4,raw[4:8].hex(),0.0,"candidate",["fixed-position 4-byte region"]))
        report.hypotheses.append("bytes[4:8] may be a length/header field; unverified")
    report.fields.append(FieldHypothesis("body_candidate",8,max(0,len(raw)-8),raw[8:].hex(),0.0,"unknown",["remaining frame after provisional prefix"]))
    report.unknown += ["field semantics","endianness","session semantics","checksum algorithm","server response format"]
    report.required_evidence += ["capture at least 3 additional PID 1026 frames","capture the server response to PID 1026","compare PID 1026 frames across different client states"]
    report.response_known = capture.response_packets > 0
    return report
