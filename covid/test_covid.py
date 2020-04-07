import pytest
import io
import click
import covid
import us
import numpy as np
import matplotlib.pyplot as plt

url2file = {
    "wsr": (
        "https://s3-us-west-1.amazonaws.com/starschema.covid/WHO_SITUATION_REPORTS.csv",
        "who_situation_reports.csv",
    ),
    "gcc": (
        "https://s3-us-west-1.amazonaws.com/starschema.covid/JHU_COVID-19.csv",
        "global_case_counts.csv",
    ),
}


def test_run():
    covid.copy_url_to_file(*url2file["gcc"])
    pass


def wa_file():
    return io.StringIO(
        """Province/State,Country/Region,Lat,Long,1/22/20,1/23/20,1/24/20
Washington,US,47.4009,-121.4905,          0,2,0
"Kitsap, WA",US,47.6477,-122.6413,        1,3,6
"Kittitas County, WA",US,47.175,-120.9319,0,1,0
Michigan,US,43.3266,-84.5361,             1,4,8
"""
    )


def xtest_03():
    f = wa_file()
    case_file = covid.read_case_file(f)
    assert case_file.dates[0] == "1/22/20"
    assert case_file.dates[2] == "1/24/20"
    assert len(case_file.case_records) == 4


def xtest_04():
    case_file = covid.read_default_case_file()
    assert len(case_file.dates) > 20
    country2states = {}
    for cr in case_file.case_records:
        l = country2states.get(cr.country, set())
        l.add(cr.state)
        country2states[cr.country] = l
    click.echo(country2states)


def xtest_05():
    f = wa_file()
    case_file = covid.read_case_file(f)
    country2state2case_record = covid.organize_cases(case_file.case_records)
    assert np.array_equal(
        country2state2case_record["US"][us.states.WA.name].cases, np.array([1, 6, 6])
    )
    assert np.array_equal(
        country2state2case_record["US"][us.states.MI.name].cases, np.array([1, 4, 8])
    )
    assert np.array_equal(
        country2state2case_record["US"][""].cases, np.array([2, 10, 14])
    )
    assert len(country2state2case_record.keys()) == 1
    assert len(country2state2case_record["US"].keys()) == 3


def xtest_06():
    f = wa_file()
    case_file = covid.read_case_file(f)
    country2state2case_record = covid.organize_cases(case_file.case_records)
    states = covid.top_states("US", country2state2case_record, 2, 0)
    assert len(states) == 2


def xtest_07():
    covid.plot_top_states("Germany", 20, 0, 10)


def xtest_06():
    case_file = covid.read_default_case_file()
    country2state2case_record = covid.organize_cases(case_file.case_records)
    country = "US"
    labels = [mdy.split("/")[1] for mdy in case_file.dates[-9:]]
    label = "Diff rom yest"
    us_states = ["", us.states.OR.name, us.states.WA.name]
    fig, axs = plt.subplots(len(us_states), 1, sharex=True)
    for (ax, state) in list(zip(axs, us_states)):
        heights = covid.diff_cases(
            country2state2case_record[country][state].cases[-10:]
        )
        # ax.bar(labels, heights, label=label)
        ax.bar(labels, heights)
        # ax.set_ylabel("Diff from previous day")
        ax.set_title(state)
        ax.legend()
    plt.show()
