import copy
import logging
import re
from functools import cache

import inperso
import pandas as pd
from fastapi import HTTPException
from inperso.atlas_index.preprocessing import compute_sla, convert_units
from inperso.atlas_index.scores import (
    ScoreContext,
    compute_scores,
    default_score_context,
)

from api.models.data import Category, Field

categories: dict[Category, list[Field]] = inperso.config.atlas_index["index_fields"]
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
    "rn": [
        "rn",
        "radon",
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
    "reverberation_time": [
        "reverberation time",
        "reverberation",
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
            # Names not covered by any pattern key (e.g. `light`) still resolve to their index category.
            field_to_category[m] = cat

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


@cache
def _get_scoreable_fields(building_type: str) -> set[str]:
    """Fields with score thresholds for a building type.

    The library scores on the residential thresholds with the building-type
    context overrides on top (see inperso.atlas_index.scores._get_thresholds),
    so a field is scoreable when either dict defines it.
    """
    thresholds = copy.deepcopy(
        inperso.config.atlas_index["thresholds"][default_score_context.building_type]
    )

    for field, params in inperso.config.atlas_index["thresholds"][
        building_type
    ].items():
        thresholds[field] = params

    return set(thresholds)


def drop_fields_without_thresholds(
    df: pd.DataFrame, context: ScoreContext
) -> pd.DataFrame:
    """Drop rows that the library scoring cannot score, and reject empty results.

    inperso-ieq drops fields without threshold parameters for the context and
    returns an error on an empty frame when every row is dropped. Temperature
    fields have no thresholds themselves: the library turns them into variant
    fields for the context and drops the outdoor rows itself.
    """
    scoreable = _get_scoreable_fields(context.building_type)
    library_handled = {"temperature", "outdoor_temperature"}

    no_threshold_fields = sorted(set(df["field"]) - scoreable - library_handled)
    if no_threshold_fields:
        logging.warning(
            f"No thresholds found for the {context.building_type} context for the fields: {no_threshold_fields}. "
            "Dropping the rows."
        )
        df = df[~df["field"].isin(no_threshold_fields)]

    if set(df["field"]) <= {"outdoor_temperature"}:
        raise HTTPException(
            status_code=400,
            detail=(
                f"None of the uploaded fields can be scored for the '{context.building_type}' building type. "
                "The upload has no fields with score thresholds for this building type."
            ),
        )

    return df


def concat_scores(
    df: pd.DataFrame,
    context: ScoreContext,
) -> tuple[pd.DataFrame, str | None]:
    fields_map, raw_fields_map = get_fields_maps(df, context.building_type)

    df["time"] = pd.to_datetime(df["time"])
    df["field"] = df["field"].apply(lambda x: fields_map[x])
    df["brand"] = df["field"].apply(lambda x: get_brand(x))
    df["device"] = ""

    df = convert_units(df)
    df = compute_light_percent(df)
    df = compute_sla(df)
    df = drop_fields_without_thresholds(df, context)

    df, fallback_note = compute_scores(df, context, keep_values=True)
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


def is_percent_of_time(raw_field: str) -> bool:
    """Check if an upload column name indicates percent-of-time values."""
    lower = raw_field.lower()
    return "percent" in lower or "%" in lower


def get_fields_maps(
    df: pd.DataFrame, building_type: str
) -> tuple[dict[str, Field], dict[Field, str]]:
    fields_map = {}
    raw_fields_map = {}

    for raw_field in df["field"].unique():
        field = get_field_name(raw_field)
        if field == "light_percent":
            if building_type == "school":
                if is_percent_of_time(raw_field):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"The field '{raw_field}' holds percent-of-time light values, which are only "
                            "scored for residential buildings. School buildings must upload light values "
                            "in lux (e.g. an 'Illuminance (lux)' or 'light' column)."
                        ),
                    )
                # Schools upload raw lux values, so map light-ish columns to
                # the school `light` field instead of the percent field.
                field = "light"
            elif not is_percent_of_time(raw_field):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"The field '{raw_field}' looks like raw light values in lux, which are only "
                        "scored for school buildings. Residential buildings must upload percent-of-time "
                        "light values (e.g. a 'light percent' column)."
                    ),
                )

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
