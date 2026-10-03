import os
import shutil
import time
import uuid

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.yara_engine import scan_with_yara
from backend.virustotal import check_virustotal_hash

from backend.database import (
    create_tables,
    save_scan,
    save_indicator,
    save_llm_report,
    get_all_scans,
)
from backend.analyzer import analyze_file
from backend.risk import calculate_risk
from backend.gemini import get_gemini_analysis

app = FastAPI(title="AI File Security Scanner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
create_tables()


@app.get("/")
def home():
    return {"message": "AI File Security Scanner API is running"}


@app.post("/scan")
def scan_file(file: UploadFile = File(...)):
    # Note: Changed from 'async def' to 'def' so synchronous CPU & network calls
    # run in Starlette's threadpool instead of blocking the main asyncio event loop.
    t_start = time.perf_counter()
    timings = {}

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, file_id)

    # 1. File Upload / Disk Write
    t0 = time.perf_counter()
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    timings["disk_write_ms"] = (time.perf_counter() - t0) * 1000

    try:
        # 2. Static Analyzer
        t0 = time.perf_counter()
        analysis = analyze_file(file_path)
        timings["analyzer_ms"] = (time.perf_counter() - t0) * 1000
        # YARA Rules Engine (Local & Instant)
        yara_result = scan_with_yara(file_path)

        # Threat Intelligence (VirusTotal Lookup)
        vt_result = check_virustotal_hash(analysis["sha256"])

        # 3. Risk Engine
        t0 = time.perf_counter()
        risk = calculate_risk(analysis, yara_results=yara_result, vt_results=vt_result)
        timings["risk_ms"] = (time.perf_counter() - t0) * 1000

        # 4. DB Storage (Scans + Indicators)
        t0 = time.perf_counter()
        scan_id = save_scan(
            filename=file.filename,
            sha256=analysis["sha256"],
            file_type=analysis["file_type"],
            file_size=os.path.getsize(file_path),
            risk_score=risk["score"],
            risk_level=risk["level"],
        )

        for reason in risk["reasons"]:
            save_indicator(
                scan_id=scan_id,
                indicator_type="Risk Indicator",
                indicator_name=reason,
                severity=risk["level"],
            )
        timings["db_save_ms"] = (time.perf_counter() - t0) * 1000

        # 5. Gemini LLM Analysis (Main Bottleneck)
        t0 = time.perf_counter()
        gemini_result = get_gemini_analysis(analysis, risk)
        timings["gemini_ms"] = (time.perf_counter() - t0) * 1000

        # 6. Save LLM Report
        if gemini_result.get("success"):
            save_llm_report(
                scan_id=scan_id,
                model=gemini_result["model"],
                report=gemini_result["report"],
            )

        total_ms = (time.perf_counter() - t_start) * 1000

        # Console Diagnostic Output
        print("\n" + "=" * 45)
        print(f"PERFORMANCE PROFILING: {file.filename}")
        print("-" * 45)
        for stage, duration in timings.items():
            pct = (duration / total_ms) * 100 if total_ms > 0 else 0
            print(f"  {stage:<18}: {duration:>8.2f} ms ({pct:>5.1f}%)")
        print("-" * 45)
        print(f"  {'TOTAL':<18}: {total_ms:>8.2f} ms")
        print("=" * 45 + "\n")

        # return {
        #     "scan_id": scan_id,
        #     "filename": file.filename,
        #     "analysis": analysis,
        #     "risk": risk,
        #     "gemini_analysis": gemini_result,
        #     "timings_ms": {k: round(v, 2) for k, v in timings.items()},
        # }
        return {
            "scan_id": scan_id,
            "filename": file.filename,
            "analysis": analysis,
            "yara": yara_result,
            "virustotal": vt_result,
            "risk": risk,
            "gemini_analysis": gemini_result,
            "timings_ms": {k: round(v, 2) for k, v in timings.items()},
        }

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.get("/scans")
def get_scans():
    return get_all_scans()