import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.yara_engine import scan_with_yara
from backend.virustotal import check_virustotal_hash

from backend.database import (
    save_scan,
    save_indicator,
    save_llm_report,
    get_all_scans,
)

from backend.analyzer import analyze_file
from backend.risk import calculate_risk
from backend.gemini import get_gemini_analysis

# Milestone 4: Google Cloud Storage integration
from backend.cloud_storage import upload_file_to_gcs


# ============================================================
# 1. FastAPI Application Configuration
# ============================================================

@asynccontextmanager
async def lifespan(app):
    yield
    from backend.database import get_pool
    if get_pool.cache_info().currsize:
        get_pool().close()


app = FastAPI(title="AI File Security Scanner", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 2. Temporary File Storage
# ============================================================

# Files are stored here only while they are being processed.
# The permanent copy is stored in Google Cloud Storage.
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/scanner-uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# 3. PostgreSQL Database Initialization
# ============================================================

# Verify that the required PostgreSQL tables exist.
# Schema is managed separately; pod startup must not depend on database availability.
from backend.health import router as health_router
app.include_router(health_router)


# ============================================================
# 4. Health Check Endpoint
# ============================================================

@app.get("/")
def home():
    return {
        "message": "AI File Security Scanner API is running"
    }


# ============================================================
# 5. File Scanning Endpoint
# ============================================================

@app.post("/scan")
def scan_file(file: UploadFile = File(...)):

    # Synchronous CPU and network operations run in
    # FastAPI's threadpool instead of blocking the event loop.

    t_start = time.perf_counter()
    timings = {}

    # Generate a unique identifier for each uploaded file.
    file_id = str(uuid.uuid4())

    # Temporary local file path used for analysis.
    file_path = os.path.join(UPLOAD_FOLDER, file_id)

    try:

        # ====================================================
        # Step 1: Save File Temporarily
        # ====================================================

        t0 = time.perf_counter()

        with open(file_path, "wb") as buffer:
            max_bytes = int(os.getenv("MAX_UPLOAD_BYTES", "20971520"))
            total = 0
            while chunk := file.file.read(65536):
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(status_code=413, detail="File exceeds upload limit")
                buffer.write(chunk)

        timings["disk_write_ms"] = (
            time.perf_counter() - t0
        ) * 1000

        # ====================================================
        # Step 2: Upload File to Google Cloud Storage
        # ====================================================

        # The Cloud Storage client automatically uses
        # Application Default Credentials (ADC).
        #
        # On Compute Engine, ADC uses the VM's attached
        # service account.
        #
        # No JSON key file is required.

        t0 = time.perf_counter()

        gcs_uri = upload_file_to_gcs(
            local_file_path=file_path,
            file_id=file_id,
            original_filename=file.filename or "unnamed",
        )

        timings["gcs_upload_ms"] = (
            time.perf_counter() - t0
        ) * 1000

        print(
            f"File uploaded to Cloud Storage: {gcs_uri}"
        )

        # ====================================================
        # Step 3: Static File Analysis
        # ====================================================

        t0 = time.perf_counter()

        analysis = analyze_file(file_path)

        timings["analyzer_ms"] = (
            time.perf_counter() - t0
        ) * 1000

        # ====================================================
        # Step 4: YARA Rules Engine
        # ====================================================

        yara_result = scan_with_yara(file_path)

        # ====================================================
        # Step 5: VirusTotal Threat Intelligence
        # ====================================================

        vt_result = check_virustotal_hash(
            analysis["sha256"]
        )

        # ====================================================
        # Step 6: Risk Calculation
        # ====================================================

        t0 = time.perf_counter()

        risk = calculate_risk(
            analysis,
            yara_results=yara_result,
            vt_results=vt_result,
        )

        timings["risk_ms"] = (
            time.perf_counter() - t0
        ) * 1000

        # ====================================================
        # Step 7: Save Scan Results to PostgreSQL
        # ====================================================

        t0 = time.perf_counter()

        scan_id = save_scan(
            filename=file.filename,
            sha256=analysis["sha256"],
            file_type=analysis["file_type"],
            file_size=os.path.getsize(file_path),
            risk_score=risk["score"],
            risk_level=risk["level"],
        )

        # Save individual risk indicators.
        for reason in risk["reasons"]:

            save_indicator(
                scan_id=scan_id,
                indicator_type="Risk Indicator",
                indicator_name=reason,
                severity=risk["level"],
            )

        timings["db_save_ms"] = (
            time.perf_counter() - t0
        ) * 1000

        # ====================================================
        # Step 8: Gemini AI Analysis
        # ====================================================

        t0 = time.perf_counter()

        gemini_result = get_gemini_analysis(
            analysis,
            risk,
        )

        timings["gemini_ms"] = (
            time.perf_counter() - t0
        ) * 1000

        # ====================================================
        # Step 9: Save Gemini Report to PostgreSQL
        # ====================================================

        if gemini_result.get("success"):

            save_llm_report(
                scan_id=scan_id,
                model=gemini_result["model"],
                report=gemini_result["report"],
            )

        # ====================================================
        # Step 10: Performance Monitoring
        # ====================================================

        total_ms = (
            time.perf_counter() - t_start
        ) * 1000

        print("\n" + "=" * 45)
        print(
            f"PERFORMANCE PROFILING: {file.filename}"
        )
        print("-" * 45)

        for stage, duration in timings.items():

            pct = (
                (duration / total_ms) * 100
                if total_ms > 0
                else 0
            )

            print(
                f"  {stage:<18}: "
                f"{duration:>8.2f} ms "
                f"({pct:>5.1f}%)"
            )

        print("-" * 45)

        print(
            f"  {'TOTAL':<18}: "
            f"{total_ms:>8.2f} ms"
        )

        print("=" * 45 + "\n")

        # ====================================================
        # Step 11: Return Scan Results
        # ====================================================

        return {
            "scan_id": scan_id,
            "filename": file.filename,
            "analysis": analysis,
            "yara": yara_result,
            "virustotal": vt_result,
            "risk": risk,
            "gemini_analysis": gemini_result,
            "timings_ms": {
                k: round(v, 2)
                for k, v in timings.items()
            },
        }

    finally:

        # ====================================================
        # Step 12: Remove Temporary Local File
        # ====================================================

        # The original uploaded file remains in Cloud Storage.
        # Only the temporary processing copy is deleted.

        if os.path.exists(file_path):
            os.remove(file_path)

        file.file.close()


# ============================================================
# 6. Retrieve Scan History
# ============================================================

@app.get("/scans")
def get_scans():
    return get_all_scans()
