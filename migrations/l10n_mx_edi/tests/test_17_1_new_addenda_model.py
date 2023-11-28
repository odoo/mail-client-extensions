try:
    from odoo import Command
except ImportError:
    # old odoo version, ignore the error as the test only runs for saas~17.1 changes
    Command = None
from odoo.addons.base.maintenance.migrations.account.tests.test_common import (
    TestAccountingSetupCommon,
)
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~17.1")
class TestL10nMxEDINewAddendaModel(TestAccountingSetupCommon):
    def prepare(self):
        results = super().prepare(chart_template_ref="mx")

        self.env.company.country_id = self.env.ref("base.mx")
        addenda = self.env["ir.ui.view"].create(
            {
                "name": "test_invoice_cfdi_addenda",
                "l10n_mx_edi_addenda_flag": True,
                "type": "qweb",
                "arch": """
                <t t-name="l10n_mx_edi.test_invoice_cfdi_addenda">
                    <test info="this is an addenda"/>
                </t>
            """,
            }
        )
        partner = self.env["res.partner"].browse(results["config"]["partner_id"])
        partner.l10n_mx_edi_addenda = addenda
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_date": "2023-09-30",
                "invoice_line_ids": [
                    Command.create({"price_unit": 100, "account_id": results["config"]["account_receivable_id"]})
                ],
            }
        )
        return {
            "related_invoice_id": invoice.id,
            "previous_addenda": {"name": addenda.name, "arch": addenda.arch},
            **results,
        }

    def check(self, init):
        partner_with_addenda = self.env["res.partner"].browse(init["config"]["partner_id"])
        invoice = self.env["account.move"].browse(init["related_invoice_id"])
        addenda = partner_with_addenda.l10n_mx_edi_addenda_id

        self.assertRecordValues(
            addenda,
            [
                {
                    "name": init["previous_addenda"]["name"],
                    "arch": init["previous_addenda"]["arch"],
                }
            ],
        )
        self.assertRecordValues(
            invoice,
            [
                {
                    "l10n_mx_edi_addenda_id": addenda.id,
                }
            ],
        )
