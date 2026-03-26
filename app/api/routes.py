from io import BytesIO

import pandas as pd
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from app.pipeline import run_analysis

router = APIRouter()


@router.post("/analyze", response_class=StreamingResponse)
async def analyze_csv(
    file: UploadFile = File(...),
    show_execution_order: bool = Form(False),
) -> StreamingResponse:
    content = await file.read()
    dataframe = pd.read_csv(BytesIO(content))

    pdf_bytes = run_analysis(
        dataframe=dataframe,
        dataset_name=file.filename or "dataset",
        show_execution_order=show_execution_order,
    )
    headers = {"Content-Disposition": f'attachment; filename="{file.filename}.report.pdf"'}
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)
