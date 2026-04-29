"""
utils/season.py — Indian season detection by calendar month.

Summer  -> March-June
Monsoon -> July-September
Winter  -> October-February
"""

from __future__ import annotations
import datetime
from config.settings import SEASON_MAP, SEASONAL_VEGETABLES, SEASONAL_FRUITS


def get_current_season() -> str:
    return SEASON_MAP.get(datetime.datetime.now().month, "winter")


def get_seasonal_vegetables(season: str | None = None) -> list[str]:
    season = season or get_current_season()
    return SEASONAL_VEGETABLES.get(season, SEASONAL_VEGETABLES["winter"])


def get_seasonal_fruits(season: str | None = None) -> list[str]:
    season = season or get_current_season()
    return SEASONAL_FRUITS.get(season, SEASONAL_FRUITS["winter"])


def get_season_label(season: str) -> str:
    return {"summer": "☀️ Summer", "monsoon": "🌧️ Monsoon", "winter": "❄️ Winter"}.get(season, season.title())
