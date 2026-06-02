import re
from functools import cache

import inperso
import pandas as pd

from api.models.data import Category, Field

categories: dict[Category, Field] = inperso.config.atlas_index["index_fields"]
patterns: dict[Field, list[str]] = {
    "co2": [
        "co2",
        "co_2",
        "co_{2}",
        "carbon dioxide",
        "carbon dioxyde",
    ],
    "pm25": [
        "pm2.5",
        "pm_{2.5}",
        "pm_2.5",
        "pm25",
        "fine particulate matter",
    ],
    "pm10": [
        "pm10",
        "pm_{10}",
        "pm_10",
        "coarse particulate matter",
    ],
    "o3": [
        "o3",
        "o_3",
        "o_{3}",
        "ozone",
    ],
    "ch2o": [
        "ch2o",
        "ch_{2}o",
        "ch_2o",
        "formaldehyde",
    ],
    "humidity": [
        "humidity",
        "relative humidity",
        "r.h.",
        "r. h.",
        "rh",
    ],
    "no2": [
        "no2",
        "no_2",
        "no_{2}",
        "nitrogen dioxide",
    ],
    "so2": [
        "so2",
        "so_2",
        "so_{2}",
        "sulfur dioxide",
    ],
    "co": [
        "co",
        "carbon monoxide",
    ],
    "temperature": [
        "temperature",
        "temp",
    ],
    "light_percent": [
        "light percent",
        "illuminance",
        "light",
        "lux",
        "lighting",
    ],
    "sla": [
        "sla",
        "sound pressure",
        "sound",
        "db(a)",
        "noise",
        "acoustic",
    ],
}
category_names = {
    "iaq": "Air quality",
    "thermal": "Thermal Comfort",
    "lux": "Lighting",
    "noise": "Acoustics",
}


@cache
def _get_field_to_category() -> dict[Field, Category]:
    field_to_category: dict[Field, Category] = {}

    for cat, meas_list in categories.items():
        for m in meas_list:
            for key in patterns:
                if m == key or m.startswith(key):
                    field_to_category[key] = cat

    return field_to_category


@cache
def _get_compiled_patterns() -> dict[Field, list[re.Pattern]]:
    compiled_patterns: dict[Field, list[re.Pattern]] = {}

    for field, field_patterns in patterns.items():
        compiled_patterns[field] = []
        for pattern in field_patterns:
            escaped = "[ _-]".join(re.escape(part) for part in pattern.split(" "))
            regex = rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])"
            compiled_patterns[field].append(re.compile(regex, re.IGNORECASE))

    return compiled_patterns


def concat_scores(df: pd.DataFrame) -> pd.DataFrame:
    return df


@cache
def get_field_name_and_category(
    raw_field_name: str,
) -> tuple[Field | None, Category | None]:
    for field, compiled_regexes in _get_compiled_patterns().items():
        for regex in compiled_regexes:
            if regex.search(raw_field_name):
                return field, _get_field_to_category()[field]

    return None, None


def compute_score(
    value: float,
    field: Field,
) -> float:
    return 0
