import pytest

from api.services.data import get_field_name_and_category


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
        # boundary: non-alphanumeric delimiters
        ("_co2_", ("co2", "iaq")),
        ("[pm2.5]", ("pm25", "iaq")),
        # boundary: alphanumeric neighbours must NOT match
        ("xco2x", None),
        ("abcO3def", None),
    ],
)
def test_get_field_name(raw_field_name, expected):
    result = get_field_name_and_category(raw_field_name)
    if expected is None:
        assert result[0] is None and result[1] is None
    else:
        assert result == expected
