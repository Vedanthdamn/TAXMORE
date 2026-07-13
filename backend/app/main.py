import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.engine.compare import RegimeComparison, compare_regimes
from app.engine.models import SalaryInput
from app.optimizer.optimizer import OptimizationResult, OptimizerInput, run_optimizer

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/calculate", response_model=RegimeComparison)
def calculate(salary: SalaryInput) -> RegimeComparison:
    return compare_regimes(salary)


@app.post("/optimize", response_model=OptimizationResult)
def optimize(params: OptimizerInput) -> OptimizationResult:
    return run_optimizer(params)
