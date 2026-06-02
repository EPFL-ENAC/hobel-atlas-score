import io
import logging

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from api.services.data import concat_scores


logger = logging.getLogger("uvicorn.error")
router = APIRouter()


@router.post(
    "/score",
    description="Add category and score columns to the provided table and returns a csv.",
)
async def score_file(
    file: UploadFile = File(...),
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

    df = concat_scores(df)

    stream = io.StringIO()
    df.to_csv(stream, index=False)

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="data.csv"'},
    )
