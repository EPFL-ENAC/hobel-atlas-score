import io
import logging
from typing import Literal

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from inperso.atlas_index.scores import ScoreContext

from api.services.data import concat_scores

logger = logging.getLogger("uvicorn.error")
router = APIRouter()

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
MAX_ROWS = 2_000_000


@router.post(
    "/score",
    description="Add category and score columns to the provided table and returns a csv.",
)
async def score_file(
    file: UploadFile = File(...),
    building_type: Literal["residential", "school"] = "residential",
    cooling_type: Literal["natural", "mechanical"] = "natural",
    heating_season: Literal["heating", "non-heating", "mixed"] = "mixed",
    heating_season_start: str | None = None,
    heating_season_end: str | None = None,
    occupancy_start_hour: int | None = None,
    occupancy_end_hour: int | None = None,
) -> Response:
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                "File is too large. "
                f"The maximum size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
            ),
        )
    df = None

    if file.filename and file.filename.lower().endswith(".xlsx"):
        try:
            df = pd.read_excel(io.BytesIO(content), nrows=MAX_ROWS + 1)
        except Exception:
            logger.exception("Failed to read uploaded file as xlsx")
            raise HTTPException(status_code=400, detail="Invalid xlsx file.")
    else:
        for sep in [",", ";", " "]:
            try:
                df = pd.read_csv(
                    io.StringIO(content.decode("utf-8")), sep=sep, nrows=MAX_ROWS + 1
                )
                break
            except Exception:
                continue

        if df is None:
            logger.exception("Failed to read uploaded file as CSV")
            raise HTTPException(
                status_code=400,
                detail="Invalid file. Supported formats: CSV (comma, semicolon, or space-separated), xlsx.",
            )

    if len(df) > MAX_ROWS:
        raise HTTPException(
            status_code=413,
            detail=f"File has too many rows. The maximum is {MAX_ROWS}.",
        )

    if "score" not in df.columns:
        try:
            if heating_season == "mixed" and not (
                heating_season_start and heating_season_end
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Heating season start and end are required when coverage is 'mixed'.",
                )
            if building_type == "school" and (
                (occupancy_start_hour is None) != (occupancy_end_hour is None)
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Occupancy start and end hours must be provided together.",
                )
            context = ScoreContext(
                building_type=building_type,
                cooling_type=cooling_type,
                heating_season=heating_season,
                heating_season_start=heating_season_start,
                heating_season_end=heating_season_end,
                occupancy_start_hour=occupancy_start_hour,
                occupancy_end_hour=occupancy_end_hour,
            )
            df, fallback_note = concat_scores(df, context)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    else:
        fallback_note = None

    stream = io.StringIO()
    df.to_csv(stream, index=False)

    headers: dict[str, str] = {
        "Content-Disposition": 'attachment; filename="data.csv"',
    }
    if fallback_note:
        headers["X-ATLAS-Fallback-Note"] = fallback_note

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers=headers,
    )
