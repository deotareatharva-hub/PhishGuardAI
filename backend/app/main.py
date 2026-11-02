
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

from backend.app.predict import predict_url
from backend.app.database import (
    initialize_database,
    save_scan,
    get_recent_scans,
    get_scan_statistics,
)


# Initialize FastAPI.
app = FastAPI(
    title="PhishGuard-AI API",
    description="AI-powered URL phishing detection service",
    version="1.1.0",
)


# Allow requests from the local React development server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    url: HttpUrl = Field(
        ...,
        description="The URL to analyze",
    )


# Create the database table when the application starts.
@app.on_event("startup")
def startup_event():
    initialize_database()


@app.get("/")
def home():
    return {
        "message": "Welcome to PhishGuard-AI API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": "SVD + MLP (14 features)",
        "database": "SQLite",
    }


@app.post("/api/scan")
def scan_url(request: ScanRequest):
    try:
        # Run the existing trained model.
        result = predict_url(str(request.url))

        # Save the prediction in SQLite.
        scan_id = save_scan(result)

        # Include the database ID in the response.
        result["scan_id"] = scan_id

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Log the underlying exception in the backend terminal.
        print(f"URL scanning failed: {exc}")

        raise HTTPException(
            status_code=500,
            detail="URL scanning failed. Check the backend logs.",
        ) from exc


@app.get("/api/history")
def scan_history(
    limit: int = Query(default=50, ge=1, le=500)
):
    try:
        scans = get_recent_scans(limit)

        return {
            "total_returned": len(scans),
            "scans": scans,
        }

    except Exception as exc:
        print(f"Failed to retrieve scan history: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve scan history.",
        ) from exc


@app.get("/api/statistics")
def scan_statistics():
    try:
        return get_scan_statistics()

    except Exception as exc:
        print(f"Failed to retrieve scan statistics: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve scan statistics.",
        ) from exc
