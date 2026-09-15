import pandas as pd
import pytest
from fastapi import HTTPException
from inperso.atlas_index.scores import ScoreContext

from api.services.data import (
    concat_scores,
    drop_fields_without_thresholds,
    get_category,
    get_field_name,
    get_fields_maps,
    is_percent_of_time,
)


@pytest.mark.parametrize(
    "raw_field_name, expected",
    [
        # co2
        ("co2", ("co2", "iaq")),
        ("CO2", ("co2", "iaq")),
        ("CO_2", ("co2", "iaq")),
        ("carbon dioxide", ("co2", "iaq")),
        ("carbon dioxyde", ("co2", "iaq")),
        ("carbon-dioxide", ("co2", "iaq")),
        # csv examples
        ("Carbon dioxide (CO_{2}) (ppm)", ("co2", "iaq")),
        # pm25
        ("PM2.5", ("pm25", "iaq")),
        ("pm_2.5", ("pm25", "iaq")),
        ("pm25", ("pm25", "iaq")),
        ("Fine particulate matter (PM_{2.5}) (µg/m^{3})", ("pm25", "iaq")),
        ("fine particulate matter", ("pm25", "iaq")),
        ("fine-particulate-matter", ("pm25", "iaq")),
        # pm10
        ("pm10", ("pm10", "iaq")),
        ("Coarse particulate matter (PM_{10}) (µg/m^{3})", ("pm10", "iaq")),
        ("pm_10", ("pm10", "iaq")),
        ("coarse particulate matter", ("pm10", "iaq")),
        # o3
        ("ozone", ("o3", "iaq")),
        ("O3", ("o3", "iaq")),
        ("Ozone (O_{3}) (µg/m^{3})", ("o3", "iaq")),
        ("O_3", ("o3", "iaq")),
        # ch2o
        ("formaldehyde", ("ch2o", "iaq")),
        ("CH2O", ("ch2o", "iaq")),
        ("ch_2o", ("ch2o", "iaq")),
        ("Formaldehyde (CH_{2}O) (µg/m^{3})", ("ch2o", "iaq")),
        # humidity
        ("relative humidity", ("humidity", "iaq")),
        ("relative-humidity", ("humidity", "iaq")),
        ("r.h.", ("humidity", "iaq")),
        ("r. h.", ("humidity", "iaq")),
        ("rh", ("humidity", "iaq")),
        ("Relative humidity (R.H.) (%)", ("humidity", "iaq")),
        # no2
        ("nitrogen dioxide", ("no2", "iaq")),
        ("nitrogen-dioxide", ("no2", "iaq")),
        ("NO2", ("no2", "iaq")),
        ("NO_2", ("no2", "iaq")),
        # so2
        ("sulfur dioxide", ("so2", "iaq")),
        ("sulfur-dioxide", ("so2", "iaq")),
        ("SO2", ("so2", "iaq")),
        ("SO_2", ("so2", "iaq")),
        # co
        ("carbon monoxide", ("co", "iaq")),
        ("carbon-monoxide", ("co", "iaq")),
        ("CO", ("co", "iaq")),
        # rn
        ("Radon (Bq/m3)", ("rn", "iaq")),
        ("radon", ("rn", "iaq")),
        ("radon-concentration", ("rn", "iaq")),
        # temperature
        ("temperature", ("temperature", "thermal")),
        ("TEMP", ("temperature", "thermal")),
        ("Temperature (°C)", ("temperature", "thermal")),
        # light_percent
        ("illuminance", ("light_percent", "lux")),
        ("Illuminance (% above/below thresholds)", ("light_percent", "lux")),
        ("light percent", ("light_percent", "lux")),
        ("light-percent", ("light_percent", "lux")),
        ("lux", ("light_percent", "lux")),
        ("lighting", ("light_percent", "lux")),
        # sla
        ("sla", ("sla", "noise")),
        ("Sound pressure (dB(A))", ("sla", "noise")),
        ("sound pressure", ("sla", "noise")),
        ("SOUND-PRESSURE", ("sla", "noise")),
        ("db(a)", ("sla", "noise")),
        ("acoustic", ("sla", "noise")),
        ("noise", ("sla", "noise")),
        # reverberation_time
        ("Reverberation time (s)", ("reverberation_time", "noise")),
        ("reverberation time", ("reverberation_time", "noise")),
        ("reverberation", ("reverberation_time", "noise")),
        # occupancy (used to filter school light rows, not scored)
        ("occupancy", ("occupancy", None)),
        ("occupied", ("occupancy", None)),
        # boundary: non-alphanumeric delimiters
        ("_co2_", ("co2", "iaq")),
        ("[pm2.5]", ("pm25", "iaq")),
        # boundary: alphanumeric neighbours must NOT match
        ("xco2x", None),
        ("abcO3def", None),
        ("xradonx", None),
    ],
)
def test_get_field_name(raw_field_name, expected):
    if expected is None:
        with pytest.raises(HTTPException):
            field = get_field_name(raw_field_name)
    else:
        field = get_field_name(raw_field_name)
        category = get_category(field)

        assert (field, category) == expected


def test_to_number():
    from api.services.data import to_number

    assert to_number(0.0) == 0.0
    assert to_number("1") == 1.0
    assert to_number(100) == 100.0

    # Occupancy values that are not numbers are kept for the library truthiness check.
    assert to_number(True) is True
    assert to_number("true") == "true"
    assert to_number("false") == "false"


def test_get_category_light():
    assert get_category("light") == "lux"


def test_is_percent_of_time():
    assert is_percent_of_time("light percent")
    assert is_percent_of_time("Illuminance (% above/below thresholds)")
    assert not is_percent_of_time("Illuminance (lux)")


def test_get_fields_maps_school_light():
    df = pd.DataFrame({"field": ["CO2", "Illuminance (lux)"]})

    fields_map, raw_fields_map = get_fields_maps(df, "school")

    assert fields_map == {"CO2": "co2", "Illuminance (lux)": "light"}
    assert raw_fields_map == {"co2": "CO2", "light": "Illuminance (lux)"}


def test_get_fields_maps_school_percent():
    df = pd.DataFrame({"field": ["light percent"]})

    with pytest.raises(HTTPException):
        get_fields_maps(df, "school")


def test_get_fields_maps_residential_light():
    df = pd.DataFrame({"field": ["Illuminance (lux)"]})

    with pytest.raises(HTTPException):
        get_fields_maps(df, "residential")


def test_get_fields_maps_residential_percent():
    df = pd.DataFrame({"field": ["CO2", "light percent"]})

    fields_map, raw_fields_map = get_fields_maps(df, "residential")

    assert fields_map == {"CO2": "co2", "light percent": "light_percent"}
    assert raw_fields_map == {
        "co2": "CO2",
        "light_percent_day": "light percent",
        "light_percent_night": "light percent",
    }


def test_concat_scores_school_light():
    df = pd.DataFrame(
        {
            "time": ["2024-01-10T10:00:00", "2024-01-10T10:00:00"],
            "field": ["co2", "Illuminance (lux)"],
            "value": [500.0, 800.0],
            "device": ["", ""],
        }
    )
    context = ScoreContext(
        building_type="school", cooling_type="mechanical", heating_season="non-heating"
    )

    df, note = concat_scores(df, context)

    # co2: 500 ppm <= 800 -> 100. light: school lux thresholds are
    # greater with 1000/750/500, so 800 lux -> 60.
    assert note is None
    assert set(df["field"]) == {"co2", "Illuminance (lux)"}
    scores = dict(zip(df["field"], df["score"]))
    categories = dict(zip(df["field"], df["category"]))
    assert scores["co2"] == pytest.approx(100)
    assert scores["Illuminance (lux)"] == pytest.approx(60)
    assert categories["co2"] == "Air quality"
    assert categories["Illuminance (lux)"] == "Lighting"


def test_concat_scores_school_light_with_occupancy():
    df = pd.DataFrame(
        {
            "time": [
                "2024-01-10T10:00:00",
                "2024-01-10T19:00:00",
                "2024-01-10T21:00:00",
                "2024-01-10T10:00:00",
                "2024-01-10T19:00:00",
            ],
            "field": ["Illuminance (lux)"] * 3 + ["occupancy"] * 2,
            "value": [1000.0, 1000.0, 1000.0, 0.0, 1.0],
            "device": ["", "", "", "", ""],
        }
    )
    context = ScoreContext(
        building_type="school", cooling_type="mechanical", heating_season="non-heating"
    )

    df, note = concat_scores(df, context)

    # The occupancy value decides per row: the occupied light row is kept even
    # outside the occupancy hours (1000 lux scores 100), the others are
    # dropped. The occupancy rows are not in the result.
    assert note is None
    assert set(df["field"]) == {"Illuminance (lux)"}
    assert df["time"].dt.hour.tolist() == [19]
    assert df["score"].iloc[0] == pytest.approx(100.0)


def test_concat_scores_school_light_without_occupancy():
    df = pd.DataFrame(
        {
            "time": ["2024-01-10T10:00:00", "2024-01-10T19:00:00"],
            "field": ["Illuminance (lux)", "Illuminance (lux)"],
            "value": [1000.0, 1000.0],
            "device": ["", ""],
        }
    )
    context = ScoreContext(
        building_type="school", cooling_type="mechanical", heating_season="non-heating"
    )

    df, note = concat_scores(df, context)

    # Without occupancy data, light rows outside the occupancy hours (8-18)
    # are dropped.
    assert df["time"].dt.hour.tolist() == [10]


def test_concat_scores_occupancy_only_rejected():
    df = pd.DataFrame(
        {
            "time": ["2024-01-10T10:00:00"],
            "field": ["occupancy"],
            "value": [1.0],
            "device": [""],
        }
    )
    context = ScoreContext(
        building_type="school", cooling_type="mechanical", heating_season="non-heating"
    )

    with pytest.raises(HTTPException) as exc_info:
        concat_scores(df, context)

    assert exc_info.value.status_code == 400


def test_concat_scores_residential_occupancy_ignored():
    df = pd.DataFrame(
        {
            "time": ["2024-01-10T10:00:00", "2024-01-10T10:00:00"],
            "field": ["light percent", "occupancy"],
            "value": [60.0, 0.0],
            "device": ["", ""],
        }
    )
    context = ScoreContext(
        building_type="residential",
        cooling_type="mechanical",
        heating_season="non-heating",
    )

    df, note = concat_scores(df, context)

    # Residential light scores are percent-of-time values; the occupancy rows
    # are ignored. A light percent value of 60 scores 100 (day thresholds).
    assert set(df["field"]) == {"light percent"}
    assert df["score"].iloc[0] == pytest.approx(100.0)


def test_concat_scores_residential_light_percent():
    df = pd.DataFrame(
        {
            "time": ["2024-01-10T10:00:00", "2024-01-10T23:00:00"],
            "field": ["light percent", "light percent"],
            "value": [60.0, 20.0],
            "device": ["", ""],
        }
    )
    context = ScoreContext(
        building_type="residential",
        cooling_type="mechanical",
        heating_season="non-heating",
    )

    df, note = concat_scores(df, context)

    # Residential percent-of-time thresholds: day greater with 60/40/10,
    # night smaller with 0/50/90.
    assert note is None
    assert len(df) == 2
    scores = df.set_index(df["time"].dt.hour)["score"]
    assert scores.loc[10] == pytest.approx(100.0)
    assert scores.loc[23] == pytest.approx(80.0)


def test_concat_scores_school_percent_only_rejected():
    df = pd.DataFrame(
        {
            "time": ["2024-01-10T10:00:00", "2024-01-10T23:00:00"],
            "field": ["light percent", "light percent"],
            "value": [60.0, 20.0],
            "device": ["", ""],
        }
    )
    context = ScoreContext(
        building_type="school", cooling_type="mechanical", heating_season="non-heating"
    )

    with pytest.raises(HTTPException) as exc_info:
        concat_scores(df, context)

    assert exc_info.value.status_code == 400
    assert "lux" in exc_info.value.detail


def test_concat_scores_residential_radon_only_scored():
    df = pd.DataFrame(
        {
            "time": ["2024-01-10T10:00:00"],
            "field": ["Radon (Bq/m3)"],
            "value": [150.0],
            "device": [""],
        }
    )
    context = ScoreContext(
        building_type="residential",
        cooling_type="mechanical",
        heating_season="non-heating",
    )

    df, note = concat_scores(df, context)

    # The residential rn thresholds are 100/200/300 Bq/m3, so 150 Bq/m3
    # scores 75.
    assert note is None
    assert len(df) == 1
    assert set(df["field"]) == {"Radon (Bq/m3)"}
    assert df["score"].iloc[0] == pytest.approx(75.0)
    assert df["category"].iloc[0] == "Air quality"


def test_concat_scores_residential_scores_radon_with_co2():
    df = pd.DataFrame(
        {
            "time": ["2024-01-10T10:00:00", "2024-01-10T10:00:00"],
            "field": ["Radon (Bq/m3)", "co2"],
            "value": [150.0, 500.0],
            "device": ["", ""],
        }
    )
    context = ScoreContext(
        building_type="residential",
        cooling_type="mechanical",
        heating_season="non-heating",
    )

    df, note = concat_scores(df, context)

    # The residential rn thresholds are 100/200/300 Bq/m3, so 150 Bq/m3
    # scores 75. A co2 value of 500 ppm is below the high-score boundary and
    # scores 100.
    assert set(df["field"]) == {"Radon (Bq/m3)", "co2"}
    scores = dict(zip(df["field"], df["score"]))
    assert scores["Radon (Bq/m3)"] == pytest.approx(75.0)
    assert scores["co2"] == pytest.approx(100.0)


def test_drop_fields_without_thresholds_rejects_outdoor_only():
    df = pd.DataFrame(
        {
            "time": ["2024-01-10T10:00:00"],
            "field": ["outdoor temperature"],
            "value": [15.0],
            "device": [""],
        }
    )
    context = ScoreContext(
        building_type="school", cooling_type="natural", heating_season="heating"
    )

    with pytest.raises(HTTPException):
        drop_fields_without_thresholds(df, context)
