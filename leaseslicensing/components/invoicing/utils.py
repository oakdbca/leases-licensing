"""
When making invoicing calculations in the leases and licensing system there are 2 main time perdiods
that may be useful depending on the type of charge method being used.

1. Financial year - 1st July to 30th June (financial quarters are also important)
2. Sequential year - 12 months from the start date of the approval
(i.e. If an approval starts on the 5th of April 2030 the last day of that sequential year is the 4th of April 2031)

"""
import calendar
import datetime
import logging
import math

from dateutil.relativedelta import relativedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


def years_elapsed_since(date):
    return relativedelta(timezone.now(), date).years


def financial_quarter_label(quarter):
    return ["JUL-SEP", "OCT-DEC", "JAN-MAR", "APR-JUN"][quarter - 1]


def financial_quarter_from_date(date):
    month = date.month
    if month in [1, 2, 3]:
        return 3
    elif month in [4, 5, 6]:
        return 4
    elif month in [7, 8, 9]:
        return 1
    elif month in [10, 11, 12]:
        return 2


def month_from_quarter(quarter):
    """Returns the month number for the start of the financial quarter provided (0 indexed)"""
    return [10, 1, 4, 7][quarter - 1]


def month_from_cpi_quarter(quarter: int) -> int:
    """CPI quarters work differently to financial quarters.
    1 = 3 (MAR Quarter), 2 = 6 (JUN Quarter), 3 = 9 (SEP Quarter), 4 = 12 (DEC Quarter)
    """
    return quarter * 3


def month_string_from_date(date):
    return month_string_from_month(date.month)


def month_string_from_month(month):
    return [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ][month - 1]


def financial_year_from_date(date):
    if not isinstance(date, datetime.date):
        raise ValueError("Date must be a datetime.date object")
    month = date.month
    year = date.year
    if month < 7:
        return f"{year - 1}-{year}"
    else:
        return f"{year}-{year + 1}"


def ordinal_suffix_of(i):
    j = i % 10
    k = i % 100
    if j == 1 and k != 11:
        return "%sst" % i
    if j == 2 and k != 12:
        return "%snd" % i
    if j == 3 and k != 13:
        return "%srd" % i
    return "%sth" % i


def sequential_year_has_passed(date):
    return date.year < timezone.now().year


def financial_year_has_passed(financial_year):
    """Takes a financial year in the format '2030-2031'
    and returns True if the current date is after the end of that financial year"""
    end_of_financial_year = timezone.datetime.strptime(
        financial_year.split("-")[1], "%Y"
    ).replace(month=6, day=30, tzinfo=timezone.utc)
    return timezone.now() > end_of_financial_year


def financial_quarter_has_passed(financial_quarter):
    """Takes a financial quarter in the format (3, 'Q3', 2021, '2020-2021')
    and returns True if the current date is after the end of that financial quarter"""
    start_month = month_from_quarter(financial_quarter[0] - 1)
    end_month = start_month + 2
    calendar_year = financial_quarter[2]
    start_of_financial_quarter = timezone.datetime.strptime(
        f"{calendar_year}-{start_month}-1", "%Y-%m-%d"
    ).replace(tzinfo=timezone.utc)
    end_of_financial_quarter = start_of_financial_quarter + relativedelta(months=2)
    end_of_financial_quarter = end_of_financial_quarter.replace(
        day=calendar.monthrange(calendar_year, end_month)[1]
    ).date()
    return timezone.now().date() > end_of_financial_quarter


def financial_years_included_in_range(start_date, end_date):
    """Returns a list of financial years included in the date range provided.
    The date range is inclusive of the start date and end date.
    """
    financial_years = []
    for year in range(start_date.year, end_date.year + 1):
        financial_years.append(f"{year}-{year + 1}")
    return financial_years


def financial_quarters_included_in_range(start_date, end_date):
    """Returns a list of financial quarters included in the date range provided.
    The date range is inclusive of the start date and end date.
    """
    financial_quarters = []
    for year in range(start_date.year, end_date.year + 1):
        for quarter in range(1, 5):
            financial_year = f"{year}-{year + 1}"
            month_for_quarter = month_from_quarter(quarter - 1)  # 0 indexed
            if quarter in [1, 2]:
                calendar_year = year
            else:
                calendar_year = year + 1
            if (
                not datetime.date(calendar_year, month_for_quarter, start_date.day)
                >= start_date
                or not datetime.date(calendar_year, month_for_quarter, end_date.day)
                <= end_date
            ):
                continue
            financial_quarters.append(
                (quarter, f"Q{quarter}", calendar_year, financial_year)
            )
    return financial_quarters


def months_included_in_range(start_date, end_date):
    """Returns a list of months included in the date range provided.
    The date range is inclusive of the start date and end date.
    """
    months = []
    for year in range(start_date.year, end_date.year + 1):
        for month_index in range(1, 13):
            if (
                not datetime.date(year, month_index, start_date.day) >= start_date
                or not datetime.date(year, month_index, end_date.day) <= end_date
            ):
                continue

            months.append(datetime.date(year, month_index, 1))
    return months


def end_of_next_financial_year(date):
    """Return the last day of the financial year after the date provided"""
    end_of_next_financial_year = (
        timezone.datetime.strptime(f"{date.year}", "%Y")
        .replace(month=6, day=30, tzinfo=timezone.utc)
        .date()
    )
    if not end_of_next_financial_year > date:
        return end_of_next_financial_year + relativedelta(years=1)
    return end_of_next_financial_year


def end_of_next_financial_quarter(date, start_month=3):
    """Return the last day of the financial quarter after the date provided"""
    quarters = quarters_from_start_month(start_month)

    for quarter in quarters:
        end_of_quarter = datetime.datetime(
            date.year,
            quarter,
            calendar.monthrange(date.year, quarter)[1],
            tzinfo=timezone.utc,
        ).date()
        if end_of_quarter > date:
            return end_of_quarter
    year = date.year + 1
    quarter = quarters[0]
    end_of_quarter = datetime.datetime(
        year, quarter, calendar.monthrange(year, quarter)[1]
    ).date()
    return end_of_quarter


def end_of_month(date):
    return date.replace(day=calendar.monthrange(date.year, date.month)[1])


def quarters_from_start_month(start_month):
    if start_month > 3:
        raise ValueError("Start month must be between 1 and 3")
    return [start_month + i * 3 for i in range(0, 4)]


def dates_overlap(datetime1, datetime2):
    return datetime1[0] <= datetime2[1] and datetime2[0] <= datetime1[1]


def years_in_date_range(start_date, end_date):
    # relative delta in years rounded up a year
    relative_delta = relativedelta(start_date, end_date)
    remainder = (
        relative_delta.days
        + relative_delta.hours
        + relative_delta.minutes
        + relative_delta.seconds
        + relative_delta.microseconds
    )
    if remainder > 0:
        return relative_delta.years + 1
    return relative_delta.years


def days_difference(start_date, end_date):
    return abs((start_date - end_date).days + 1)


def months_difference(start_date, end_date):
    relative_delta = relativedelta(start_date, end_date)
    return abs((relative_delta.years * 12) + relative_delta.months)


def quarters_difference(start_date, end_date):
    return abs(math.ceil(months_difference(start_date, end_date) / 3))


def years_difference(start_date, end_date):
    return abs(math.ceil(months_difference(start_date, end_date) / 12))
