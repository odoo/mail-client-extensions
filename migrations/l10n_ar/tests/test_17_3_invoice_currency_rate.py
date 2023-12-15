from odoo.addons.base.maintenance.migrations.account.tests.test_17_3_invoice_currency_rate import (
    TestMoveInvoiceCurrencyRateCommon,
)
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~17.3")
class TestMoveInvoiceCurrencyRateAR(TestMoveInvoiceCurrencyRateCommon):
    def prepare(self):
        res = {}

        # Create new dedicated currencies to avoid issues with currency rates without company_id.
        currency = self.env["res.currency"].create(
            [
                {
                    "name": "AR0",
                    "symbol": "AR0",
                }
            ]
        )
        company = self.env["res.company"].create(
            {
                "name": "invoice_currency_rate test company AR",
                "country_id": self.env.ref("base.ar").id,
                "currency_id": currency.id,
            }
        )
        self.env["account.chart.template"].try_loading("ar_ri", company=company, install_demo=False)

        # Create moves without field 'l10n_ar_currency_rate' set.
        # They should not be treated any differently just because the moves belong to an AR company.
        currency2 = self.env["res.currency"].create(
            [
                {
                    "name": "AR1",
                    "symbol": "AR1",
                }
            ]
        )
        expected_rate = self._prepare_moves(company, currency2)
        res["expected_rates_list"] = [expected_rate]

        # Create moves with field 'l10n_ar_currency_rate' set.
        # For multi-currency invoices the rates should be computed from that field.
        currency3 = self.env["res.currency"].create(
            [
                {
                    "name": "AR2",
                    "symbol": "AR2",
                }
            ]
        )
        currency3.active = True
        expected_rate = self._prepare_moves(company, currency3)
        for move_id, old_rate in expected_rate.items():
            move = self.env["account.move"].browse([move_id])
            if move.move_type != "entry" and move.currency_id != move.company_id.currency_id:
                new_rate = old_rate + 10
                move.l10n_ar_currency_rate = 1 / new_rate
                expected_rate[move_id] = new_rate

        res["expected_rates_list"].append(expected_rate)

        return res
