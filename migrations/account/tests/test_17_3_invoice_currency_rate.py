import datetime

from pytz import timezone

from odoo import fields

try:
    from odoo import Command
except ImportError:
    Command = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestMoveInvoiceCurrencyRateCommon(UpgradeCase, abstract=True):
    def _get_company_account(self, company, domain):
        return company.env["account.account"].search(
            [
                *self.env["account.account"]._check_company_domain(company),
                *domain,
            ],
            limit=1,
        )

    def _fetch_rate(self, invoice):
        return self.env["res.currency"]._get_conversion_rate(
            invoice.company_id.currency_id, invoice.currency_id, invoice.company_id or None, invoice.invoice_date
        )

    def _prepare_moves(self, company, currency2):
        """Return a dictionary (move.id -> expected invoice_currency_rate) containing all moves created in this function."""
        account_income = self._get_company_account(company, [("account_type", "=", "income")])
        account_receivable = self._get_company_account(company, [("account_type", "=", "asset_receivable")])

        # Returned dictionary (move.id -> expected invoice_currency_rate) containing all moves created in this function.
        expected_rate = {}

        # Create a non-invoice move.
        move = company.env["account.move"].create(
            {
                "move_type": "entry",
                "company_id": company.id,
                "line_ids": [
                    (0, 0, {"account_id": account_income.id, "credit": 200}),
                    (0, 0, {"account_id": account_receivable.id, "debit": 200}),
                ],
            }
        )
        expected_rate[move.id] = False

        # Ensure there is a rate for the company currency during the time of the created moves.
        company_rate_start_date = datetime.datetime(
            year=2000, month=1, day=1, hour=0, minute=0, second=0, tzinfo=timezone("utc")
        )
        if not company.env["res.currency.rate"].search_count(
            [("company_id", "=", company.root_id.id), ("name", "=", company_rate_start_date)], limit=1
        ):
            company.env["res.currency.rate"].create(
                {
                    "name": company_rate_start_date,
                    "company_id": company.root_id.id,
                    "currency_id": company.currency_id.id,
                    "rate": 2,
                }
            )

        invoice_date = datetime.datetime(year=2020, month=8, day=27, hour=0, minute=0, second=0, tzinfo=timezone("utc"))

        invoice_vals = {
            "company_id": company.id,
            "currency_id": company.currency_id.id,
            "invoice_date": invoice_date,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                Command.create(
                    {
                        "quantity": 1,
                        "account_id": account_income.id,
                        "price_unit": 100,
                        "tax_ids": [],
                    }
                ),
            ],
        }
        invoice_vals_zero_total = {
            **invoice_vals,
            "invoice_line_ids": [
                Command.create(
                    {
                        "quantity": 1,
                        "account_id": account_income.id,
                        "price_unit": 0,
                        "tax_ids": [],
                    }
                ),
            ],
        }

        # Domestic invoices
        move = company.env["account.move"].create(invoice_vals)
        expected_rate[move.id] = 1
        move = company.env["account.move"].create(invoice_vals_zero_total)
        expected_rate[move.id] = 1

        # Multi-currency invoices

        # Set up rates around the invoice date to ensure we fetch the correct rates.
        invoice_date_rate_vals = {
            # There will be no rate on invoice_date for company.root_id
            "name": fields.Datetime.add(invoice_date, days=-1),
            "company_id": company.root_id.id,
            "currency_id": currency2.id,
            "rate": 8,
        }
        first_rate = company.env["res.currency.rate"].create(
            {
                **invoice_date_rate_vals,
                "name": fields.Datetime.add(invoice_date, days=-2),
                "rate": 100,
            }
        )
        rate_on_invoice_date = company.env["res.currency.rate"].create(invoice_date_rate_vals)
        company.env["res.currency.rate"].create(
            {
                **invoice_date_rate_vals,
                "name": invoice_date,  # This should not be used instead of rate_on_invoice_date.
                "company_id": False,
                "rate": 8000,
            }
        )
        last_rate = company.env["res.currency.rate"].create(
            {
                **invoice_date_rate_vals,
                "name": fields.Datetime.add(invoice_date, days=1),
                "rate": 1000,
            }
        )

        move = company.env["account.move"].create(
            {
                **invoice_vals,
                "currency_id": currency2.id,
            }
        )
        move0 = company.env["account.move"].create(
            {
                **invoice_vals_zero_total,
                "currency_id": currency2.id,
            }
        )
        # Changing the rate used for 'move' should not change the computed rate.
        # (Since we compute it from the totals for invoices with non-0 total.)
        # But it will change the rate for move0 (fetched at at the end of this function).
        rate_on_invoice_date.rate = 4
        expected_rate[move.id] = abs(move.amount_total / move.amount_total_signed)

        first_rate_move0 = company.env["account.move"].create(
            {
                **invoice_vals_zero_total,
                "invoice_date": first_rate.name,
                "currency_id": currency2.id,
            }
        )

        last_rate_move0 = company.env["account.move"].create(
            {
                **invoice_vals_zero_total,
                "invoice_date": last_rate.name,
                "currency_id": currency2.id,
            }
        )

        # Ensure we fallback to rates without company_id if needed
        company.env["res.currency.rate"].create(
            {
                **invoice_date_rate_vals,
                "name": fields.Datetime.add(invoice_date, years=-1),
                "company_id": False,
                "rate": 10000,
            }
        )
        move_null_company_rate = company.env["account.move"].create(
            {
                **invoice_vals_zero_total,
                "invoice_date": fields.Datetime.add(invoice_date, years=-1),
                "currency_id": currency2.id,
            }
        )

        # Check move before the first rate
        move_before_rates = company.env["account.move"].create(
            {
                **invoice_vals_zero_total,
                "invoice_date": fields.Datetime.add(company_rate_start_date, days=-1),
                "currency_id": currency2.id,
            }
        )

        # For invoices with 0 total we will fetch the rate.
        # We do it here since now all rates are set (and should not be changed anymore).
        expected_rate[move0.id] = self._fetch_rate(move0)
        expected_rate[first_rate_move0.id] = self._fetch_rate(first_rate_move0)
        expected_rate[last_rate_move0.id] = self._fetch_rate(last_rate_move0)
        expected_rate[move_null_company_rate.id] = self._fetch_rate(move_null_company_rate)
        expected_rate[move_before_rates.id] = self._fetch_rate(move_before_rates)
        self.assertTrue(expected_rate[move_before_rates.id] == 1)  # (roughly) check it is before any rate

        return expected_rate

    def prepare(self):
        # Override this function (c.f. `TestMoveInvoiceCurrencyRate.prepare`)
        return {"expected_rates_list": []}

    def _check_expected_rates(self, expected_rates_list):
        for expected_rate in expected_rates_list:
            moves = self.env["account.move"].browse([int(move_id) for move_id in expected_rate])
            self.assertRecordValues(moves, [{"invoice_currency_rate": expected_rate[str(move.id)]} for move in moves])

    def check(self, init):
        self._check_expected_rates(init["expected_rates_list"])


@change_version("saas~17.3")
class TestMoveInvoiceCurrencyRate(TestMoveInvoiceCurrencyRateCommon):
    def _prepare_move_only_fallback_rates(self, currency2):
        no_rate_currency = self.env["res.currency"].create(
            [
                {
                    "name": "CR2",
                    "symbol": "CR2",
                }
            ]
        )
        company = self.env["res.company"].create(
            {
                "name": "invoice_currency_rate test no company currency rate company",
                "country_id": self.env.ref("base.us").id,
                "currency_id": no_rate_currency.id,
            }
        )
        self.env["account.chart.template"].try_loading("generic_coa", company=company, install_demo=False)
        account_income = self._get_company_account(company, [("account_type", "=", "income")])

        invoice_date = datetime.datetime(year=2020, month=8, day=27, hour=0, minute=0, second=0, tzinfo=timezone("utc"))

        invoice = company.env["account.move"].create(
            {
                "company_id": company.id,
                "currency_id": currency2.id,
                "invoice_date": invoice_date,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "quantity": 1,
                            "account_id": account_income.id,
                            "price_unit": 0,
                            "tax_ids": [],
                        }
                    ),
                ],
            }
        )

        return {invoice.id: self._fetch_rate(invoice)}

    def prepare(self):
        # Create new dedicated currencies to avoid issues with currency rates without company_id.
        currency = self.env["res.currency"].create(
            [
                {
                    "name": "CR0",
                    "symbol": "CR0",
                }
            ]
        )
        root_company = self.env["res.company"].create(
            {
                "name": "invoice_currency_rate test parent company",
                "country_id": self.env.ref("base.us").id,
                "currency_id": currency.id,
            }
        )
        self.env["account.chart.template"].try_loading("generic_coa", company=root_company, install_demo=False)
        company = self.env["res.company"].create(
            {
                "name": "invoice_currency_rate test company",
                "country_id": self.env.ref("base.us").id,
                "parent_id": root_company.id,
            }
        )
        self.env["account.chart.template"].try_loading("generic_coa", company=company, install_demo=False)

        currency2 = self.env["res.currency"].create(
            [
                {
                    "name": "CR1",
                    "symbol": "CR1",
                }
            ]
        )

        return {
            "expected_rates_list": [
                self._prepare_moves(company, currency2),
                self._prepare_move_only_fallback_rates(currency2),
            ]
        }
