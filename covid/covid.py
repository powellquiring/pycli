import click
import json
import subprocess
import urllib.request
import urllib.parse
import shutil
import ssl
import csv
import numpy as np
import us
from dataclasses import dataclass
from typing import List
import matplotlib.pyplot as plt

# url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
confirmed_csv = "confirmed.csv"


@dataclass
class CaseRecord:
    state: str
    country: str
    latitude: float
    longitude: float
    cases: List[int]


@dataclass
class CaseFile:
    state: str
    country: str
    latitude: str
    longitude: str
    dates: List[str]
    case_records: List[CaseRecord]


def string_is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def read_case_file(csvfile):
    confirmed_rows = csv.reader(csvfile)
    case_file = None
    case_records = []
    for row in confirmed_rows:
        try:
            if confirmed_rows.line_num == 1:
                case_file = CaseFile(row[0], row[1], row[2], row[3], row[4:], [])
                continue
            # extra comma on some
            if not string_is_int(row[-1]):
                row[-1] = row[-2]
            cases = np.array(row[4:]).astype(np.int)
            if cases[-1] == cases[-2]:
                cases[-1] = cases[-1] + (cases[-2] - cases[-3])
            case_record = CaseRecord(
                row[0],
                row[1],
                float(row[2]),
                float(row[3]),
                # np.array(row[4:]).astype(np.int),
                cases,
            )
            case_records.append(case_record)
        except Exception as e:
            click.echo(e)
    case_file.case_records = case_records
    return case_file


def us_city_record(case_record):
    "return the state for a us city record or None if not a us city record"
    if case_record.country == "US":
        city_state = case_record.state.split(",")
        if len(city_state) == 2:
            state_str = city_state[1].strip()
            state = us.states.lookup(state_str)
            if state == None:
                click.echo(f"state string not valid: {state_str}")
                return None
            else:
                return state.name
    return None


def add_more_cases_to_case_record(existing_case_record, new_case_record):
    existing_case_record.cases = np.add(
        existing_case_record.cases, new_case_record.cases
    )


def make_country_case_record_for_country_with_states(case_record):
    return CaseRecord(case_record.country, "", 0.0, 0.0, 0)


def add_more_cases_to_country_record(country2state2case_record, case_record):
    if not "" in country2state2case_record[case_record.country]:
        country2state2case_record[case_record.country][
            ""
        ] = make_country_case_record_for_country_with_states(case_record)
    add_more_cases_to_case_record(
        country2state2case_record[case_record.country][""], case_record
    )


def organize_cases(case_records: List[CaseRecord]) -> List[CaseRecord]:
    "take the raw case records and create a map of countries[state] with an empty state rolling up the country"
    country2state2case_record = (
        {}
    )  # returning the [country][state]: CaseRecord for that state
    us_state2cases_for_cities = {}  # state to cases accumulator
    for case_record in case_records:
        state = us_city_record(case_record)
        if state != None:
            # US city record, add it to the state
            assert state in country2state2case_record["US"]
            add_more_cases_to_case_record(
                country2state2case_record["US"][state], case_record
            )
            add_more_cases_to_country_record(country2state2case_record, case_record)
            continue

        if not case_record.country in country2state2case_record:
            country2state2case_record[case_record.country] = {}
        assert not case_record.state in country2state2case_record[case_record.country]
        country2state2case_record[case_record.country][case_record.state] = case_record
        if case_record.state != "":
            add_more_cases_to_country_record(country2state2case_record, case_record)
    return country2state2case_record


def read_default_case_file():
    with open(confirmed_csv) as csvfile:
        return read_case_file(csvfile)


def diff_cases(cases):
    return np.array([cases[i + 1] - cases[i] for i in range(len(cases) - 1)])


def sum_cases(cases):
    values = np.array([a for a in cases.values()])
    return values.sum(axis=0)


def dump(state_cases):
    us_cases = np.array([])
    for (state, cases) in state_cases.items():
        if len(us_cases) == 0:
            us_cases = cases
        else:
            us_cases = np.add(us_cases, cases)
        click.echo(f"{state} {cases[-1]}")
    click.echo(us_cases)


def get():
    gcontext = ssl.SSLContext()
    with urllib.request.urlopen(url, context=gcontext) as f:
        s = f.read().decode("utf-8")
        with open(confirmed_csv, "w") as out:
            out.write(s)


import requests


def copy_url_to_file(url: str, file: str):
    r = requests.get(url, stream=True)
    with open(file, "wb") as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)


# def copy_url_to_file(url: str, file: str):
#    gcontext = ssl.SSLContext()
#    with urllib.request.urlopen(url, context=gcontext) as response:
#        response_str = response.read().decode("utf-8")
#        with open(file, "w") as out:
#            shutil.copyfileobj(response_str, out)


def top_states(country, country2state2case_record, top, skip):
    state_cases = [
        (state, case_record.cases[-1])
        for (state, case_record) in country2state2case_record[country].items()
    ]
    state_cases.sort(key=lambda state_case: state_case[1], reverse=True)
    return [state_case[0] for state_case in state_cases[skip:top]]


def plot_top_states(country, top, skip, days):
    click.echo(f"{top}, {skip}")
    case_file = read_default_case_file()
    country2state2case_record = organize_cases(case_file.case_records)
    label = "Diff rom yest"
    states = top_states(country, country2state2case_record, top, skip) + [
        us.states.OR.name
    ]
    states = top_states(country, country2state2case_record, top, skip)
    if country == "US":
        states = states + [us.states.OR.name]
    labels = [mdy.split("/")[1] for mdy in case_file.dates[-(days - 1) :]]
    xs = case_file.dates[-(days - 1) :]
    xs = [s.split("/")[1] for s in xs]
    for state in states:
        heights = diff_cases(country2state2case_record[country][state].cases[-days:])
        # plt.plot(case_file.dates[-(days - 1) :], heights)
        plt.plot(xs, heights)
    if states[0] == "":
        states[0] = country
    plt.legend(states)
    plt.show()


def plot_us_state(state, days):
    case_file = read_default_case_file()
    country2state2case_record = organize_cases(case_file.case_records)
    country = "US"
    label = "Diff from yest"
    labels = [mdy.split("/")[1] for mdy in case_file.dates[-(days - 1) :]]
    heights = diff_cases(country2state2case_record[country][state].cases[-days:])
    plt.plot(heights)
    plt.title(state)
    plt.show()

    # for column in df.drop('x', axis=1):
    #    plt.plot(df['x'], df[column], marker='', color='grey', linewidth=1, alpha=0.4)


@click.command()
@click.option("-f", "--fetch", is_flag=True, help="fetch the contents")
@click.option("-t", "--top", type=int, default=100, help="top states")
@click.option("-ts", "--skip", type=int, help="skip the top ones")
@click.option("-s", "--state", help="pick a specific us state")
@click.option("-c", "--country", default="US", help="pick a specific country")
@click.option("-d", "--days", type=int, default=15, help="number of days to show")
def cli(fetch, top, skip, country, state, days):
    """dump covid data"""
    click.echo("covid")
    if fetch:
        get()
    if state != None:
        plot_us_state(us.states.lookup(state).name, days)
    else:
        if skip == None:
            skip = 0
        plot_top_states(country, top, skip, days)


if __name__ == "__main__":
    cli()
