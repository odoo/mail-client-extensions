from contextlib import ExitStack
from datetime import date
from unittest.mock import patch

from dateutil.relativedelta import relativedelta

try:
    from odoo import Command
except ImportError:
    Command = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import module_installed


@change_version("saas~16.5")
class TestAnalyticPlan(UpgradeCase):
    def prepare(self):
        root_analytic_plan = self.env["account.analytic.plan"].create(
            {
                "name": "Root plan",
                "parent_id": False,
            }
        )
        child_analytic_plan = self.env["account.analytic.plan"].create(
            {
                "name": "Child plan",
                "parent_id": root_analytic_plan.id,
            }
        )
        analytic_account = self.env["account.analytic.account"].create(
            {
                "name": "Test analytic account",
                "plan_id": child_analytic_plan.id,
            }
        )
        journal_data = {
            "name": "Journal Test Analytic Plan 16_5",
            "code": "AP165",
            "type": "sale",
        }
        if module_installed(self.env.cr, "l10n_latam_invoice_document"):
            journal_data["l10n_latam_use_documents"] = False

        journal = self.env["account.journal"].create(journal_data)
        partner = self.env["res.partner"].create({"name": "Some Partner"})
        product = self.env["product.product"].create({"name": "Some Product"})
        invoice_date = self.env.company._get_user_fiscal_lock_date() + relativedelta(months=1) or date.today()
        invoice = self.env["account.move"].create(
            {
                "partner_id": partner.id,
                "journal_id": journal.id,
                "move_type": "out_invoice",
                "invoice_date": invoice_date,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "price_unit": 50,
                            "analytic_distribution": {
                                analytic_account.id: 100,
                            },
                        }
                    )
                ],
            }
        )

        with ExitStack() as stack:
            if hasattr(invoice, "_check_document_types_post"):
                stack.enter_context(patch.object(type(invoice), "_check_document_types_post", lambda _: None))
            if "account.edi.format" in self.env:
                stack.enter_context(
                    patch.object(type(self.env["account.edi.format"]), "_get_move_applicability", lambda _, __: None)
                )
            invoice.action_post()

        analytic_line = invoice.invoice_line_ids.analytic_line_ids

        return {
            "analytic_line_id": analytic_line.id,
            "analytic_account_id": analytic_account.id,
            "child_analytic_plan_id": child_analytic_plan.id,
            "root_analytic_plan_id": root_analytic_plan.id,
        }

    def check(self, values):
        analytic_line = self.env["account.analytic.line"].browse(values["analytic_line_id"])
        analytic_account = self.env["account.analytic.account"].browse(values["analytic_account_id"])

        Fields = self.env["ir.model.fields"]
        analytic_line_model = self.env["ir.model"].search([("model", "=", "account.analytic.line")])

        # Check that the column for the root plan has been created
        self.assertTrue(
            Fields.search(
                [
                    ("name", "=", f"x_plan{values['root_analytic_plan_id']}_id"),
                    ("model_id", "=", analytic_line_model.id),
                ]
            )
        )

        # Check that no column for the child plan has been created
        self.assertFalse(
            Fields.search(
                [
                    ("name", "=", f"x_plan{values['child_analytic_plan_id']}_id"),
                    ("model_id", "=", analytic_line_model.id),
                ]
            )
        )

        # Check that the analytic account is still linked to the child plan
        self.assertEqual(analytic_account.plan_id.id, values["child_analytic_plan_id"])

        # Check that the analytic account is set on the root plan column
        self.assertEqual(analytic_line[f"x_plan{values['root_analytic_plan_id']}_id"].id, analytic_account.id)
