# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~13.5")
class L10nItTestRefactoringEDI(UpgradeCase):

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        company = self.env["res.company"].create({"name": "company for L10nItTestRefactoringEDI"})

        # Create user.
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "user L10nItTestRefactoringEDI",
                    "login": "L10nItTestRefactoringEDI",
                    "groups_id": [
                        (6, 0, self.env.user.groups_id.ids),
                        (4, self.env.ref("account.group_account_user").id),
                    ],
                    "company_ids": [(6, 0, company.ids)],
                    "company_id": company.id,
                }
            )
        )
        user.partner_id.email = "L10nItTestRefactoringEDI@test.com"

        chart_template = self.env.ref("l10n_it.l10n_it_chart_template_generic", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading(company=company)

        company.write(
            {
                "vat": "IT12345670017",
                "l10n_it_codice_fiscale": "IT12345670017",
                "l10n_it_tax_system": "RF01",
                "country_id": self.env.ref("base.it").id,
                "street": "Sugar Street",
                "zip": "11111",
                "city": "Sugarland",
            }
        )

        account_income = self.env["account.account"].search(
            [
                ("company_id", "=", company.id),
                ("user_type_id", "=", self.env.ref("account.data_account_type_revenue").id),
            ],
            limit=1,
        )
        account_receivable = self.env["account.account"].search(
            [
                ("company_id", "=", company.id),
                ("user_type_id.type", "=", "receivable"),
            ],
            limit=1,
        )

        product = (
            self.env["product.product"]
            .with_user(user)
            .create(
                {
                    "name": "product_L10nItTestRefactoringEDI",
                    "lst_price": 1000.0,
                    "property_account_income_id": account_income.id,
                }
            )
        )

        partner = (
            self.env["res.partner"]
            .with_user(user)
            .create(
                {
                    "name": "partnert_L10nItTestRefactoringEDI",
                    "property_account_receivable_id": account_receivable.id,
                    "vat": "IT12345670017",
                    "country_id": self.env.ref("base.it").id,
                    "street": "Chocolate Street",
                    "zip": "22222",
                    "city": "Bourg-Palette",
                }
            )
        )

        tax = (
            self.env["account.tax"]
            .with_user(user)
            .create(
                {
                    "name": "tax_15",
                    "amount_type": "percent",
                    "amount": 15,
                    "type_tax_use": "sale",
                    "company_id": company.id,
                }
            )
        )

        type_field = "move_type" if util.version_gte("saas~13.3") else "type"
        invoice = (
            self.env["account.move"]
            .with_user(user)
            .create(
                {
                    type_field: "out_invoice",
                    "partner_id": partner.id,
                    "invoice_date": "2017-01-01",
                    "date": "2017-01-01",
                    "invoice_line_ids": [(0, 0, {"product_id": product.id, "tax_ids": [(6, 0, tax.ids)]})],
                }
            )
        )
        invoice.action_post()
        edi = invoice.l10n_it_einvoice_id

        self.assertTrue(edi)

        return invoice.id, edi.id

    def check(self, init):
        move_id, attachment_id = init
        invoice = self.env["account.move"].browse(move_id)
        attachment = self.env["ir.attachment"].browse(attachment_id)

        self.assertRecordValues(invoice, [{"edi_state": "sent"}])
        self.assertRecordValues(invoice.edi_document_ids, [{"state": "sent", "attachment_id": attachment.id}])
