try:
    from odoo import Command
except ImportError:
    # old odoo version, ignore the error as the test only runs for saas~18.1 changes
    Command = None
from odoo.addons.base.maintenance.migrations.account.tests.test_common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~18.1")
class TestL10nMxEDIPaymentPolicy(TestAccountingSetupCommon):
    def prepare(self):
        results = super().prepare(chart_template_ref="mx")

        self.env.company.country_id = self.env.ref("base.mx")
        partner = self.env["res.partner"].browse(results["config"]["partner_id"])

        payment_term = self.env["account.payment.term"].create(
            {
                "name": "20 days two lines",
                "line_ids": [
                    Command.create(
                        {
                            "value_amount": 30,
                            "value": "percent",
                            "nb_days": 10,
                        }
                    ),
                    Command.create(
                        {
                            "value_amount": 70,
                            "value": "percent",
                            "nb_days": 20,
                        }
                    ),
                ],
            }
        )

        invoices = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": partner.id,
                    "invoice_date": "2023-10-01",
                    "invoice_date_due": "2023-10-10",  # PUE
                },
                {
                    "move_type": "out_invoice",
                    "partner_id": partner.id,
                    "invoice_date": "2023-10-01",
                    "invoice_date_due": "2023-11-10",  # PPD
                },
                {
                    "move_type": "out_invoice",
                    "partner_id": partner.id,
                    "invoice_date": "2023-10-01",
                    "invoice_date_due": "2023-10-10",
                    "invoice_payment_term_id": payment_term.id,  # PPD
                },
                {
                    "move_type": "out_refund",  # PUE
                    "partner_id": partner.id,
                    "invoice_date": "2023-10-01",
                    "invoice_date_due": "2023-11-10",
                },
                {
                    "move_type": "in_invoice",  # No payment policy
                    "partner_id": partner.id,
                    "invoice_date": "2023-10-01",
                    "invoice_date_due": "2023-11-10",
                },
            ]
        )
        expected_payment_policies = ["PUE", "PPD", "PPD", "PUE", False]
        self.assertRecordValues(
            invoices,
            [
                {
                    "l10n_mx_edi_payment_policy": payment_policy,
                }
                for payment_policy in expected_payment_policies
            ],
        )
        return {
            "invoice_ids": invoices.ids,
            "expected_payment_policies": expected_payment_policies,
        }

    def check(self, init):
        invoices = self.env["account.move"].browse(init["invoice_ids"])
        self.assertRecordValues(
            invoices,
            [
                {
                    "l10n_mx_edi_payment_policy": payment_policy,
                }
                for payment_policy in init["expected_payment_policies"]
            ],
        )
