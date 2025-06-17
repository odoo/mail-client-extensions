try:
    from odoo import Command
except ImportError:
    # old odoo version, ignore the error as the test only runs for saas~18.4 changes
    Command = None
from odoo.addons.base.maintenance.migrations.account.tests.test_common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~18.4")
class TestL10nCoEDIOperationType(TestAccountingSetupCommon):
    def prepare(self):
        results = super().prepare(chart_template_ref="co")

        self.env.company.country_id = self.env.ref("base.co")
        partner = self.env["res.partner"].browse(results["config"]["partner_id"])

        debit_note_journal_id = self.env["account.journal"].create(
            {
                "name": "journal_co",
                "code": "test_CO",
                "type": "sale",
                "company_id": self.company.id,
                "l10n_co_edi_dian_authorization_number": "test_dian_number",
                "l10n_co_edi_debit_note": True,
            }
        )

        def _create_move(**kwargs):
            invoice = self.env["account.move"].create(
                {
                    "partner_id": partner.id,
                    "move_type": "out_invoice",
                    "invoice_date": "2023-10-01",
                    "invoice_date_due": "2023-10-10",
                    "invoice_line_ids": [
                        Command.create({"price_unit": 100, "account_id": results["config"]["account_receivable_id"]})
                    ],
                    **kwargs,
                }
            )
            invoice.action_post()
            return invoice

        invoice_10 = _create_move()
        invoice_20 = _create_move(move_type="out_refund", reversed_entry_id=invoice_10.id)
        invoice_22 = _create_move(move_type="out_refund")

        debit_wizard = (
            self.env["account.debit.note"]
            .with_context(active_model="account.move", active_ids=invoice_10.ids)
            .create(
                {
                    "l10n_co_edi_description_code_debit": "1",
                    "copy_lines": True,
                    "reason": "The value of the product just went up",
                    "journal_id": debit_note_journal_id.id,
                }
            )
        )
        debit_wizard.create_debit()

        debit_30 = invoice_10.debit_note_ids
        debit_32 = _create_move(journal_id=debit_note_journal_id.id)

        all_invoices = invoice_10 + invoice_20 + invoice_22 + debit_30 + debit_32
        expected_operation_types = ["10", "20", "22", "30", "32"]
        self.assertRecordValues(
            all_invoices,
            [
                {
                    "l10n_co_edi_operation_type": operation_type,
                }
                for operation_type in expected_operation_types
            ],
        )

        return {"invoice_ids": all_invoices.ids, "expected_operation_types": expected_operation_types}

    def check(self, init):
        invoices = self.env["account.move"].browse(init["invoice_ids"])
        self.assertRecordValues(
            invoices,
            [
                {
                    "l10n_co_edi_operation_type": operation_type,
                }
                for operation_type in init["expected_operation_types"]
            ],
        )
