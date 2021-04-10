import os
from typing import Dict, List

import requests
from pathlib import Path
import pandas as pd
from fastapi import FastAPI
from comparator.comparator import process_guideline
from comparator.quantity import Quantity


app = FastAPI()
GUIDELINE_SERVER: str = os.environ["GUIDELINE_SERVER"]
PATIENTDATA_SERVER: str = os.environ["PATIENTDATA_SERVER"]
DATA_PATH: str = os.environ["CEOSYS_DATA_PATH"]


@app.get("/")
async def root() -> Dict:
    return {"message": "Comparator"}


def save_results(res, variables, guideline_id):
    summary = res[["valid_exposure", "valid_population", "valid_treatment"]].droplevel(
        level=1, axis=1
    )
    details = res[variables].stack("variable_name").reset_index("variable_name")
    summary.to_pickle(Path(DATA_PATH) / f"guideline_{guideline_id}_results_summary.pkl")
    details.to_pickle(Path(DATA_PATH) / f"guideline_{guideline_id}_results_detail.pkl")


@app.get("/run")
async def run() -> str:
    guideline_ids = get_guideline_ids()

    for guideline_id in guideline_ids:
        guideline = get_guideline(guideline_id)
        variables, q_population, q_exposure = process_guideline(guideline)
        data = request_data(variables)
        res = compare(data, q_population, q_exposure)
        save_results(res, variables, guideline_id)

    return "Success"


def get_guideline_ids() -> List:
    r = requests.get(GUIDELINE_SERVER + "/guideline/list")
    return [gl["id"] for gl in r.json()]


def get_guideline(guideline_id: str) -> Dict:
    r_guideline = requests.get(GUIDELINE_SERVER + f"/guideline/get/{guideline_id}")
    guideline = r_guideline.json()

    return guideline


def request_data(variables: List[str]) -> pd.DataFrame:
    r = requests.post(PATIENTDATA_SERVER + "/patients/", json=variables)

    df = pd.DataFrame(r.json())
    df = (
        df.sort_values(by="datetime").groupby(["pseudo_fallnr", "variable_name"]).nth(0)
    )
    df = df.unstack("variable_name")
    df = df.swaplevel(axis=1).sort_index(axis=1)

    return df


def compare(
    df: pd.DataFrame, q_population: List[Quantity], q_exposure: List[Quantity]
) -> pd.DataFrame:
    for q in q_population:
        df[(q.variable_name, "valid_population")] = df[
            (q.variable_name, "value")
        ].apply(q.valid)

    for q in q_exposure:
        df[(q.variable_name, "valid_exposure")] = df[(q.variable_name, "value")].apply(
            q.valid
        )

    col_population = [(q.variable_name, "valid_population") for q in q_population]
    col_exposure = [(q.variable_name, "valid_exposure") for q in q_exposure]

    df["valid_population"] = df[col_population].all(axis=1)
    df["valid_exposure"] = df[col_exposure].all(axis=1)
    df["valid_treatment"] = (df["valid_population"] & df["valid_exposure"]) | (
        ~df["valid_population"]
    )

    df = df.sort_index(axis=1)

    return df
