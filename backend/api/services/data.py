import re
from functools import cache

import inperso
import pandas as pd
from fastapi import HTTPException
from inperso.atlas_index.preprocessing import compute_sla, convert_units
from inperso.atlas_index.scores import (
    ScoreContext,
    compute_scores,
    compute_scores_with_context,
)

from api.models.data import Category, Field

categories: dict[Category, Field] = inperso.config.atlas_index["index_fields"]
patterns: dict[Field, list[str]] = {
    "outdoor_temperature": [
        "outdoor temperature",
        "outdoor temp",
        "outside temperature",
        "outside temp",
        "external temperature",
        "external temp",
        "outdoor_temp",
        "outside_temp",
        "external_temp",
    ],
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
field_variants: dict[Field, list[str]] = {
    "light_percent": ["light_percent_day", "light_percent_night"],
    "sla": [
        "sla_day",
        "sla_night",
    ],
    "temperature": [
        "temperature_cooling_nat",
        "temperature_cooling_mec",
        "temperature_heating",
    ],
}
category_names = {
    "iaq": "Air quality",
    "thermal": "Thermal comfort",
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


def concat_scores(
    df: pd.DataFrame,
    context: ScoreContext | None = None,
) -> tuple[pd.DataFrame, str | None]:
    fields_map, raw_fields_map = get_fields_maps(df)

    df["time"] = pd.to_datetime(df["time"])
    df["field"] = df["field"].apply(lambda x: fields_map[x])
    df["brand"] = df["field"].apply(lambda x: get_brand(x))
    df["device"] = ""

    df = convert_units(df)
    df = compute_light_percent(df)
    df = compute_sla(df)

    fallback_note: str | None = None

    if context is not None:
        df, fallback_note = compute_scores_with_context(df, context, keep_values=True)
    else:
        df = compute_scores(df, keep_values=True)

    df["category"] = df["field"].apply(lambda x: get_category(x))
    df["category"] = df["category"].apply(lambda x: category_names[x])
    df["field"] = df["field"].apply(lambda x: raw_fields_map[x])
    df.drop(columns=["unit_number"], inplace=True, errors="ignore")

    return df, fallback_note


def compute_light_percent(df: pd.DataFrame) -> pd.DataFrame:
    day_start_hour = inperso.config.atlas_index["sla"]["day_start_hour"]
    night_start_hour = inperso.config.atlas_index["sla"]["night_start_hour"]
    hour = df["time"].dt.hour
    is_day = (hour >= day_start_hour) & (hour < night_start_hour)
    is_light_percent = df["field"] == "light_percent"

    df.loc[is_day & is_light_percent, "field"] = "light_percent_day"
    df.loc[~is_day & is_light_percent, "field"] = "light_percent_night"

    return df


def get_fields_maps(df: pd.DataFrame) -> tuple[dict[str, Field], dict[Field, str]]:
    fields_map = {}
    raw_fields_map = {}

    for raw_field in df["field"].unique():
        field = get_field_name(raw_field)
        fields_map[raw_field] = field

        if field in field_variants:
            for field_variant in field_variants[field]:
                raw_fields_map[field_variant] = raw_field
        else:
            raw_fields_map[field] = raw_field

    return fields_map, raw_fields_map


@cache
def get_field_name(
    raw_field: str,
) -> Field:
    for field, compiled_regexes in _get_compiled_patterns().items():
        for regex in compiled_regexes:
            if regex.search(raw_field):
                return field

    raise HTTPException(status_code=400, detail=f"Unrecognized field name: {raw_field}")


@cache
def get_category(
    field: Field | None,
) -> Category | None:
    if field is None:
        return None

    for field_base, variants in field_variants.items():
        if field in variants:
            field = field_base
            break

    return _get_field_to_category().get(field, None)


@cache
def get_brand(
    field: Field | None,
) -> str | None:
    if field is None:
        return None

    for brand in inperso.config.atlas_index["fields"]:
        if field in field_variants:
            for variant in field_variants[field]:
                if variant in inperso.config.atlas_index["fields"][brand]:
                    return brand

        if field in inperso.config.atlas_index["fields"][brand]:
            return brand

    return None
