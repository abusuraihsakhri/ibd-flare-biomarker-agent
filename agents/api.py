"""
FastAPI REST API Server for Ibd Flare Biomarker Agent.
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel
from .base import AuditLogger, SecurityException, ResourceLimitExceededException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from .metrics import GLOBAL_METRICS

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Ibd Flare Biomarker Agent API",
    description="Local demonstration of generic rules; not a validated IBD clinical decision support system.",
    version="2.0.0",
)


class ChatRequest(BaseModel):
    query: str


@app.exception_handler(SecurityException)
def reject_identifier(request, exc):
    GLOBAL_METRICS.record_phi_block()
    return JSONResponse(
        status_code=400, content={"detail": "Input contains a prohibited identifier."}
    )


@app.exception_handler(ResourceLimitExceededException)
def reject_oversized(request, exc):
    return JSONResponse(
        status_code=413, content={"detail": "Input exceeds the allowed scan length."}
    )


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(Path(__file__).resolve().parents[1] / "web" / "index.html")


@app.get("/styles.css", include_in_schema=False)
def dashboard_styles():
    return FileResponse(Path(__file__).resolve().parents[1] / "web" / "styles.css", media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def dashboard_script():
    return FileResponse(Path(__file__).resolve().parents[1] / "web" / "app.js", media_type="text/javascript")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "ibd-flare-biomarker-agent", "domain": "Gastroenterology & Hepatology Systems", "rules": "UNVALIDATED_DEMONSTRATION", "version": "2.0.0"}


@app.get("/metrics")
def metrics():
    return Response(GLOBAL_METRICS.export_prometheus_text(), media_type="text/plain; version=0.0.4")


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=400, detail="Input contains a prohibited identifier.")


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
