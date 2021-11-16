from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
from typing import Optional, Dict, List, Any 
from gpr import convert, predict,update
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from fastapi import status
app = FastAPI()

templates = Jinja2Templates(directory="templates")

# pydantic models
class PredictionInput(BaseModel):
    company: str
    horizon: Optional[str]  
    frequency: Optional[str]  
    # data: Optional[List[Any]]  
class PredictionOutput(PredictionInput):
    forecast: Dict


# class StockIn(BaseModel):
#     company: str
#     horizon: Optional[str]  
#     frequency: Optional[str]  
#     # start: Optional[str]  

# class StockOut(StockIn):
#     forecast: Dict

class UpdateInput(BaseModel):
    company: str
    date: List[str]
    data: List[float]

class UpdateOutput(BaseModel):
    check: bool


# routes


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", 
    {'request': request,
    })


# @app.post("/update", response_model=UpdateOutput, status_code=status.HTTP_200_OK)
# async def update_model(payload: UpdateInput):
#     company = payload.company
#     date = payload.date
#     data = payload.data
#     check = update(company, date = date, data = data)
    
#     return check

    


@app.post("/predict", response_model=PredictionOutput, status_code=status.HTTP_200_OK)
async def get_prediction(payload: PredictionInput):
    company = payload.company
    frequency = payload.frequency
    horizon = payload.horizon
    # data = payload.data

    prediction_list = predict(company, freq = frequency, horizon = horizon,)

    if not prediction_list:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Model not found.")

    response_object = {"company": company,'frequency':frequency,'horizon':horizon, "forecast": convert(prediction_list)}
    return response_object