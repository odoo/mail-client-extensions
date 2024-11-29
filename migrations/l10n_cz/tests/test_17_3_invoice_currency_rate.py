import datetime

from pytz import timezone

from odoo import fields

from odoo.addons.base.maintenance.migrations.account.tests.test_17_3_invoice_currency_rate import (
    TestMoveInvoiceCurrencyRateCommon,
)
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~17.3")
class TestMoveInvoiceCurrencyRateCZ(TestMoveInvoiceCurrencyRateCommon):
    def prepare(self):
        res = {}

        # Create new dedicated currencies to avoid issues with currency rates without company_id.
        currency = self.env["res.currency"].create(
            [
                {
                    "name": "CZ0",
                    "symbol": "CZ0",
                }
            ]
        )
        company = self.env["res.company"].create(
            {
                "name": "invoice_currency_rate test company CZ",
                "country_id": self.env.ref("base.cz").id,
                "currency_id": currency.id,
            }
        )
        company = company.with_context(default_taxable_supply_date=False)
        self.env["account.chart.template"].try_loading("cz", company=company, install_demo=False)

        # Create moves without field 'taxable_supply_date' set.
        # They should not be treated any differently just because the moves belong to a CZ company.
        currency2 = self.env["res.currency"].create(
            [
                {
                    "name": "CZ1",
                    "symbol": "CZ1",
                }
            ]
        )
        expected_rate = self._prepare_moves(company, currency2)
        res["expected_rates_list"] = [expected_rate]

        # Create moves with field 'taxable_supply_date' set.
        # That date should be used for the conversion
        currency3 = self.env["res.currency"].create(
            [
                {
                    "name": "CZ2",
                    "symbol": "CZ2",
                }
            ]
        )
        currency3.active = True
        # The `taxable_supply_date` should be used to convert moves where the `amount_total` is 0
        taxable_supply_date = datetime.datetime(
            year=2023, month=8, day=27, hour=0, minute=0, second=0, tzinfo=timezone("utc")
        )
        # Create rates on the `taxable_supply_date` as well as the days before and after.
        company.env["res.currency.rate"].create(
            {
                "name": taxable_supply_date,
                "company_id": company.root_id.id,
                "currency_id": currency3.id,
                "rate": 200,
            }
        )
        company.env["res.currency.rate"].create(
            {
                "name": fields.Datetime.add(taxable_supply_date, days=-1),
                "company_id": company.root_id.id,
                "currency_id": currency3.id,
                "rate": 999,
            }
        )
        company.env["res.currency.rate"].create(
            {
                "name": fields.Datetime.add(taxable_supply_date, days=1),
                "company_id": company.root_id.id,
                "currency_id": currency3.id,
                "rate": 9999,
            }
        )
        expected_rate = self._prepare_moves(company, currency3)
        for move_id in expected_rate:
            move = self.env["account.move"].browse([move_id])
            if move.move_type != "entry" and move.currency_id == currency3 and move.amount_total == 0:
                move.taxable_supply_date = taxable_supply_date
                expected_rate[move_id] = self._fetch_rate(move, date=taxable_supply_date)

        res["expected_rates_list"].append(expected_rate)

        return res
