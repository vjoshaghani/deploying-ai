from langchain.tools import tool

from assignment_chat.db import open_collection
from assignment_chat.tools_attractions import search_attractions
from assignment_chat.tools_budget import calculate_plan
from assignment_chat.tools_weather import get_ottawa_weather


def build_tools():
    """Connect our existing functions to model-callable tools."""
    collection = open_collection()

    @tool("search_attractions")
    def search_tool(
        query: str,
        setting: str | None = None,
        limit: int = 3,
    ) -> list[dict]:
        """Find Ottawa attractions matching interests.

        setting may be indoor, outdoor, mixed, or omitted.
        Returns attraction IDs needed by calculate_plan.
        """
        return search_attractions(
            collection=collection,
            query=query,
            setting=setting,
            limit=limit,
        )

    @tool("get_ottawa_weather")
    def weather_tool(visit_date: str) -> dict:
        """Get Ottawa weather for YYYY-MM-DD.

        Supports today through six days ahead.
        Returns an unavailable result when no forecast can be provided.
        """
        return get_ottawa_weather(visit_date)

    @tool("calculate_plan")
    def budget_tool(
        place_ids: list[str],
        adults: int,
        budget_cad: float,
        available_minutes: int,
        meal_per_adult_cad: float,
        transport_total_cad: float,
        travel_minutes: int,
        meal_minutes: int,
        buffer_minutes: int,
    ) -> dict:
        """Calculate demo cost and duration for selected attraction IDs.

        Use IDs returned by search_attractions.
        Meals are priced per adult; transport is a total group allowance.
        Travel, meal, and buffer minutes are total durations for the group.
        Obtain the user's constraints and agreed allowances before calling.
        """
        return calculate_plan(
            place_ids=place_ids,
            adults=adults,
            budget_cad=budget_cad,
            available_minutes=available_minutes,
            meal_per_adult_cad=meal_per_adult_cad,
            transport_total_cad=transport_total_cad,
            travel_minutes=travel_minutes,
            meal_minutes=meal_minutes,
            buffer_minutes=buffer_minutes,
        )

    return [search_tool, weather_tool, budget_tool]