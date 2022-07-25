# -*- coding: utf-8 -*-
import functools
import json
from pathlib import Path

import pytz
from psycopg2.extras import execute_values

from odoo.addons.base.maintenance.migrations import util


@functools.lru_cache(maxsize=1)
def countries_with_regions(cr):
    """Return a set of country ids with dependent regions

    The same currency, phone code etc. can be shared by multiple countries. Sometimes, those countries
    will be a big country, along with some of its much smaller dependent territory, e.g. Finland
    and Åland share the same phone code. Statistically, it is more likely that the company is in Finland.

    Since we do not have country size information (population, GDP etc.), we can at least guess which
    countries are very small by looking at whether they have regions. The reasoning is:
    No regions -> probably a very small country -> far less likely to be the place of the company, compared
    to the alternative country with multiple regions (if it exists and is only one).

    ISO 3166-1 lists both indepedent countries and dependent territories, but (at least in the file
    provided at /usr/share/iso-codes/json/) doesn't give independency information. In order to
    differentiate between them, the regional subdivisions list (ISO 3166-2) is consulted. It lists
    the world's regions in the format COUNTRY_CODE-REGION_CODE.

    This is just a prioritization, rather than a strict limit. If the calling code only applies to a
    single country, then that country is picked no matter its size/regions (e.g. Liechtenstein).
    If two or more countries have regions, none of them is picked (e.g. USA and Canada).
    This heuristic is only used if multiple countries share a calling code, and only one of those
    countries has regions (e.g. UK and Guernsey/Jersey).
    """

    iso_path = "/usr/share/iso-codes/json/iso_3166-2.json"
    iso_3166_2 = Path(iso_path)
    if not iso_3166_2.is_file():
        return set()  # Empty set, will produce empty resultsets on intersections with sets of countries

    with open(iso_path, "rb") as f:
        regions_json = json.load(f)

    codes = set([country["code"].split("-")[0] for country in regions_json["3166-2"]])
    cr.execute(
        """
        SELECT id
          FROM res_country
         WHERE code IN %s
        """,
        [tuple(codes)],
    )
    return {code[0] for code in cr.fetchall()}


def clue_func(reason, prefer_big_countries=True):
    """Decorator for filtering clue functions

    Clue functions (of name, currency, phone code etc.) return a set of country ids based on the clue.
    With this decorator, each clue function gets assigned a proper string for its reason, and has its
    country_ids set filtered as follows:
    - If there is only one country_id, return it
    - If there are multiple, but the big_countries are significant, check if there is only one big_country in the set
    - If there's still zero or multiple countries in the set, return the whole set
    The first two result in the migrate() function assigning the country_id to the company
    The latter results in the migrate() function trying the next clue function, keeping the set only for informative purposes
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(cr, company_id):
            matched_countries = f(cr, company_id)

            if len(matched_countries) == 1:
                return matched_countries

            if prefer_big_countries:
                matched_big_countries = matched_countries.intersection(countries_with_regions(cr))
                if len(matched_big_countries) == 1:
                    return matched_big_countries

            # Didn't find a single country, return all of them to be at least displayed to the user as hints
            return matched_countries

        wrapper.reason = reason
        return wrapper

    return decorator


def migrate(cr, version):
    """Attempting to deduce the company's country

    The clues are examined in order of specificity, with clues that point to a single country
    (company name, timezone) being considered first, before falling back to multi-country
    clues such as currency (e.g. Euros and dollars, which are used by many countries) or TLD (while each country
    has its own TLD, people might opt for a TLD of their language, especially when their country's TLD
    is not available, e.g. *.fr email addresses for some French-speaking African countries).
    """
    cr.execute(
        """
        SELECT id
          FROM res_company
         WHERE res_company.account_tax_fiscal_country_id IS NULL
           AND EXISTS(SELECT 1 FROM account_tax WHERE account_tax.company_id = res_company.id)
        """
    )
    company_no_country_ids = [res[0] for res in cr.fetchall()]

    # Clues for finding a country, in order of precedence
    clue_funcs = [
        get_coa_country_ids,
        get_partner_country_ids,
        get_name_country_ids,
        get_tz_country_ids,
        get_phone_country_ids,
        get_journal_currency_country_ids,
        get_currency_country_ids,
        get_tld_country_ids,
        get_lang_country_ids,
    ]

    country_dict = dict()  # will hold company_id -> (country_id,reason)
    for company_id in company_no_country_ids:
        # run all clue functions on the company, and keep only the first entry with len==1
        all_country_hints = []  # will hold all non-empty hints, in case of a MigrationError
        for f in clue_funcs:
            country_ids = f(cr, company_id)
            if len(country_ids) != 0:
                all_country_hints.append((country_ids, f.reason))
            if len(country_ids) == 1:
                country_dict[company_id] = (country_ids.pop(), f.reason)
                break  # found our clue
        else:
            # no single-country candidate found for at least one company
            raise util.MigrationError(
                f"Please define a fiscal country on companies with these IDs before upgrading: {company_no_country_ids}\n"
                f"Clues found so far are ([company ID: (country ID, reason for clue)]): {all_country_hints}"
            )

    if country_dict:
        country_list = [(company_id, country) for company_id, (country, reason) in country_dict.items()]
        # Update the country in the db
        execute_values(
            cr._obj,
            """
               UPDATE res_company AS cmp
                  SET account_tax_fiscal_country_id = c.country_id
                 FROM res_country AS ctr,
                      (VALUES %s) AS c(company_id, country_id)
                WHERE cmp.id = c.company_id
                  AND ctr.id = c.country_id
            RETURNING c.company_id, cmp.name, ctr.name
            """,
            country_list,
        )

        # Building report about company:
        report_data = cr.fetchall()

        # Message for migration report, including reason for each country that has been set
        report_str = (
            f"The fiscal country was not set for companies with ids={company_no_country_ids},"
            " but is needed for the upgrade to continue. "
            "The companies' fiscal countries have been guessed based on the following clues:"
        )
        for report_res in report_data:
            report_str += (
                f"\n - Company {report_res[1]} (ID={report_res[0]}) had its country "
                f"set to {report_res[2]} based on {country_dict[report_res[0]][1]}."
            )

        report_str += (
            "\nPlease check if this change suits your needs, and if needed perform "
            "any corrections manually before performing a new upgrade request."
        )
        util.add_to_migration_reports(category="Accounting", message=report_str)


@clue_func("the Chart of Accounts")
def get_coa_country_ids(cr, company_id):
    """Returns the country id based on CoA

    Originally from pre-10.py, refactored together with other clues into separate file.
    """
    cr.execute(
        """
        SELECT country.id
          FROM res_company company, ir_model_data, res_country country
         WHERE ir_model_data.model = 'account.chart.template'
           AND ir_model_data.res_id = company.chart_template_id
           AND (
                  (   ir_model_data.module ~ '^l10n_[a-z]{2}(_.*)?$'
                  AND lower(country.code) = substring(ir_model_data.module from 6 for 2)
                  )
               OR (   ir_model_data.module = 'l10n_uk'
                  AND lower(country.code) = 'gb'
                  )
               OR (   ir_model_data.module = 'l10n_generic_coa'
                  AND lower(country.code) = 'us'
                  )
         ) AND company.id=%s;
        """,
        [company_id],
    )

    return {c[0] for c in cr.fetchall()}


@clue_func("the company's partner entry's country")
def get_partner_country_ids(cr, company_id):
    """Returns the country id based on the company's partner entry

    Originally from pre-10.py, refactored together with other clues into separate file.
    """
    cr.execute(
        """
        SELECT p.country_id
          FROM res_partner AS p
          JOIN res_company AS c ON c.partner_id = p.id
         WHERE p.country_id IS NOT NULL
           AND c.id = %s;
        """,
        [company_id],
    )

    return {c[0] for c in cr.fetchall()}


@clue_func("the country being included in the company name", False)
def get_name_country_ids(cr, company_id):
    """Returns the country whose name is a substring of the company's name.

    In the case where one country is the subword of another and multiple countries
    are matched (e.g. 'Nigeria Tech Solutions' matches both 'Niger' and 'Nigeria'),
    keep the one with the longer name.
    """
    cr.execute(
        """
          SELECT res_country.id, res_country.name
            FROM res_country,res_company
           WHERE res_company.name ~* ANY(ARRAY[res_country.name])
             AND res_company.id=%s
        ORDER BY LENGTH(res_country.name) DESC;
        """,
        [company_id],
    )

    if cr.rowcount == 0:
        return set()
    else:
        country_list = cr.fetchall()
        # If a country is a subword of another, keep the longer one:
        country_list = [c1[0] for c1 in country_list if not any([c1[1] in c2[1] for c2 in country_list if c1 != c2])]

        return {c for c in country_list}


@clue_func("the currency of the company's journals")
def get_journal_currency_country_ids(cr, company_id):
    """Returns countries whose currency is used by the company's journal.

    Multi-country currencies return all countries in the currency union.
    """
    cr.execute(
        """
            SELECT c.id
              FROM res_country AS c
        INNER JOIN account_journal AS j ON c.currency_id=j.currency_id
             WHERE j.company_id=%(company_id)s
          GROUP BY c.id;
        """,
        locals(),
    )
    return {c[0] for c in cr.fetchall()}


@clue_func("the company's currency")
def get_currency_country_ids(cr, company_id):
    """Returns countries whose currency is used by the company.

    Multi-country currencies return all countries in the currency union.
    """
    cr.execute(
        """
            SELECT ctr.id
              FROM res_country AS ctr
        INNER JOIN res_company AS cmp ON ctr.currency_id=cmp.currency_id
             WHERE cmp.id=%(company_id)s
        """,
        locals(),
    )
    return {c[0] for c in cr.fetchall()}


@clue_func("the country code of the company's phone number")
def get_phone_country_ids(cr, company_id):
    """
    Returns countries that have the same phone code as the ones listed in the company's fields.
    """
    # Get country based on phone/mobile number country code
    cr.execute(
        r"""
        SELECT res_country.id
          FROM (
            SELECT COALESCE(
                    substring(res_company.phone FROM '\+([0-9]+) '),
                    substring(res_partner.phone FROM '\+([0-9]+) '),
                    substring(res_partner.mobile FROM '\+([0-9]+) ')
                 ) AS ph_code
              FROM res_partner
              JOIN res_company ON res_company.partner_id=res_partner.id
             WHERE res_company.id=%s
        ) AS phone_codes,res_country
        WHERE ph_code=res_country.phone_code::VARCHAR;
        """,
        [company_id],
    )
    return {cid[0] for cid in cr.fetchall()}


@clue_func("the country Top Level Domain in the company's website/email address")
def get_tld_country_ids(cr, company_id):
    """
    Returns country based on the Top Level Domain code of:
    a) the company's website or, if unavailable
    b) the company's email address
    Only TLDs of length 2 are considered, to match the countries' alpha-2 code
    but not the generic 3-character TLDs like .com, .net etc.

    A special provision needs to be made for the UK, whose country code is 'gb'
    but still uses the TLD of 'uk'.
    """
    cr.execute(
        r"""
        SELECT res_country.id
          FROM (
            SELECT CASE
                WHEN COALESCE(
                    substring(res_partner.website FROM '\.([^\.]{2})$'),
                    substring(res_company.email FROM '\.([^\.]{2})$'),
                    substring(res_partner.email FROM '\.([^\.]{2})$')
                )='uk'
                THEN 'gb'
                ELSE COALESCE(
                    substring(res_partner.website FROM '\.([^\.]{2})$'),
                    substring(res_company.email FROM '\.([^\.]{2})$'),
                    substring(res_partner.email FROM '\.([^\.]{2})$')
                ) END c_code
            FROM res_partner
            JOIN res_company ON res_company.partner_id=res_partner.id
           WHERE res_company.id=%s
        ) AS email_codes,res_country
        WHERE LOWER(c_code)=LOWER(res_country.code)
        """,
        [company_id],
    )

    return {c[0] for c in cr.fetchall()}


@clue_func("the company's timezone")
def get_tz_country_ids(cr, company_id):
    """Returns country of supplied timezone.

    Some timezones (usually the ones involving a city in their name) are linked to a specific country.
    If that link exists, we can deduce the country based on the timezone's name. No guess can be made
    for more general timezone names like 'UTC-1' though - the country-timezone mapping is taken from
    pytz.
    """

    # Create mapping timezones->countries:
    # pytz offers only countries->timezones, so we have to reverse it
    tz_c_dict = [(tz, k) for k, tz in pytz.country_timezones.items()]
    # ...and create the new tuple pairs
    tz_tuples = tuple([(tz_name, country[1]) for country in tz_c_dict for tz_name in country[0]])

    # Get country of partner's tz
    cr.execute(
        """
        SELECT y.id
          FROM res_company AS c, res_partner AS p, res_country AS y
         WHERE c.partner_id=p.id
           AND c.id=%s
           AND (p.tz,y.code) IN %s
        """,
        [company_id, tz_tuples],
    )

    return {c[0] for c in cr.fetchall()}


@clue_func("the company's language locale")
def get_lang_country_ids(cr, company_id):
    """Returns country of company's language locale.

    The company's language locale is noted of the form xx_YY, where xx is the language code
    and YY is the country's alpha-2 code. This allows for a direct deduction of the country,
    however it will often be set wrongly (oftentimes en_US is used in place of the real language).
    It should thus be consulted only as a last resort.
    """
    cr.execute(
        """
        SELECT y.id
          FROM res_company AS c, res_partner AS p, res_country AS y
         WHERE p.country_id IS NULL
           AND c.id=%s
           AND c.partner_id=p.id
           AND substring(p.lang FROM '_([A-Z]{2})$')=UPPER(y.code);
        """,
        [company_id],
    )

    return {c[0] for c in cr.fetchall()}
