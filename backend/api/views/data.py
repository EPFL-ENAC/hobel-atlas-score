import io
import logging
from typing import Literal

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from api.services.data import ScoreContext, concat_scores

logger = logging.getLogger("uvicorn.error")
router = APIRouter()


@router.post(
    "/score",
    description="Add category and score columns to the provided table and returns a csv.",
)
async def score_file(
    file: UploadFile = File(...),
    building_type: Literal["residential", "school"] | None = None,
    cooling_type: Literal["natural", "mechanical"] | None = None,
    heating_season: Literal["heating", "non-heating", "mixed"] | None = None,
    heating_season_start: str | None = None,
    heating_season_end: str | None = None,
) -> Response:
    content = await file.read()
    df = None

    if file.filename and file.filename.lower().endswith(".xlsx"):
        try:
            df = pd.read_excel(io.BytesIO(content))
        except Exception:
            logger.exception("Failed to read uploaded file as xlsx")
            raise HTTPException(status_code=400, detail="Invalid xlsx file.")
    else:
        for sep in [",", ";", " "]:
            try:
                df = pd.read_csv(io.StringIO(content.decode("utf-8")), sep=sep)
                break
            except Exception:
                continue

        if df is None:
            logger.exception("Failed to read uploaded file as CSV")
            raise HTTPException(
                status_code=400,
                detail="Invalid file. Supported formats: CSV (comma, semicolon, or space-separated), xlsx.",
            )

    context: ScoreContext | None = None
    if (
        building_type is not None
        or cooling_type is not None
        or heating_season is not None
    ):
        if building_type is None or cooling_type is None or heating_season is None:
            raise HTTPException(
                status_code=400,
                detail="Building type, cooling/conditionning type, and heating-season coverage must all be provided.",
            )
        if heating_season == "mixed" and not (
            heating_season_start and heating_season_end
        ):
            raise HTTPException(
                status_code=400,
                detail="Heating season start and end are required when coverage is 'mixed'.",
            )
        context = ScoreContext(
            building_type=building_type,
            cooling_type=cooling_type,
            heating_season=heating_season,
            heating_season_start=heating_season_start,
            heating_season_end=heating_season_end,
        )

    if "score" not in df.columns:
        try:
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
