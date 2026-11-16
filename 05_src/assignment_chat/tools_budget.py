from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parent / "data" / "attractions.csv"


def calculate_plan(
    place_ids,
    adults,
    budget_cad,
    available_minutes,
    meal_per_adult_cad,
    transport_total_cad,
    travel_minutes,
    meal_minutes,
    buffer_minutes,
):
    """Calculate a group's demo cost and duration for selected attractions."""
    if not place_ids:
        raise ValueError("Select at least one attraction.")

    if len(place_ids) != len(set(place_ids)):
        raise ValueError("Each attraction should appear only once.")

    if isinstance(adults, bool) or not isinstance(adults, int) or adults < 1:
        raise ValueError("Adults must be a positive whole number.")

    values = [
        budget_cad,
        available_minutes,
        meal_per_adult_cad,
        transport_total_cad,
        travel_minutes,
        meal_minutes,
        buffer_minutes,
    ]

    if any(value < 0 for value in values):
        raise ValueError("Costs and durations cannot be negative.")

    attractions = pd.read_csv(DATA_PATH).set_index("place_id")

    unknown_ids = set(place_ids) - set(attractions.index)
    if unknown_ids:
        raise ValueError(f"Unknown attraction IDs: {sorted(unknown_ids)}")

    selected = attractions.loc[place_ids]

    admission_total = round(
        float(selected["adult_admission_cad"].sum()) * adults, 2
    )
    meal_total = round(meal_per_adult_cad * adults, 2)

    total_cost = round(
        admission_total + meal_total + transport_total_cad, 2
    )

    visit_minutes = int(selected["suggested_visit_minutes"].sum())

    total_minutes = (
        visit_minutes
        + travel_minutes
        + meal_minutes
        + buffer_minutes
    )

    remaining_budget = round(budget_cad - total_cost, 2)
    remaining_minutes = available_minutes - total_minutes

    return {
        "attractions": selected["name"].tolist(),
        "adults": adults,
        "admission_total_cad": admission_total,
        "meal_total_cad": meal_total,
        "transport_total_cad": transport_total_cad,
        "total_cost_cad": total_cost,
        "total_minutes": total_minutes,
        "remaining_budget_cad": remaining_budget,
        "remaining_minutes": remaining_minutes,
        "fits_budget": remaining_budget >= 0,
        "fits_time": remaining_minutes >= 0,
    }