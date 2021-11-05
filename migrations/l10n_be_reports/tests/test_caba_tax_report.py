# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~12.3")
class TestCABATaxReport(UpgradeCase):
    def prepare(self):
        eur = self.env.ref("base.EUR")
        be_chart_template = self.env.ref("l10n_be.l10nbe_chart_template")

        # create test company with Belgian CoA
        company = self.env["res.company"].create(
            {
                "name": "World Company",
                "currency_id": eur.id,
                "tax_exigibility": True,
                "country_id": self.env.ref("base.be").id,
            }
        )
        self.env.user.company_id = company
        be_chart_template.try_loading_for_current_company()

        # Configure test taxes
        caba_account_id = self.env["account.account"].create(
            {
                "name": "Test tax caba account",
                "code": "MIG_tax_caba_acc",
                "user_type_id": self.env.ref("account.data_account_type_current_assets").id,
                "company_id": company.id,
            }
        )

        # Those xmlids are created at CoA installation
        tax_sale = self.env.ref("l10n_be.%s_attn_VAT-OUT-21-S" % company.id)
        tax_purchase = self.env.ref("l10n_be.%s_attn_VAT-IN-V81-21" % company.id)

        test_taxes = tax_sale + tax_purchase
        test_taxes.write({"tax_exigibility": "on_payment", "cash_basis_account_id": caba_account_id.id})

        # Generate invoices
        inv_line_account = self.env["account.account"].create(
            {
                "name": "Test invoice line account",
                "code": "MIG_caba_inv_line",
                "user_type_id": self.env.ref("account.data_account_type_current_assets").id,
                "company_id": company.id,
            }
        )

        mig_check_data = {"company_id": company.id, "tax_report_by_date": {}}
        for test_tax in test_taxes:

            # Create an invoice with a CABA tax and pay it
            self.create_invoice(company, 100, test_tax, "2015-01-01", inv_line_account, pay=True)

            # Create a refund with a CABA tax and pay it
            self.create_invoice(company, 100, test_tax, "2015-01-02", inv_line_account, pay=True, refund=True)

            # Create an invoice with a CABA tax and a negative line and pay it
            self.create_invoice(company, 100, test_tax, "2015-01-03", inv_line_account, pay=True, negate_half=True)

            # Create a refund with a CABA tax and a negative line and pay it
            self.create_invoice(
                company, 100, test_tax, "2015-01-04", inv_line_account, pay=True, refund=True, negate_half=True
            )

            # Create an invoice with a CABA tax and refund it
            inv_to_refund = self.create_invoice(company, 100, test_tax, "2015-01-05", inv_line_account)
            refund_wizard = (
                self.env["account.invoice.refund"]
                .with_context(active_ids=inv_to_refund.ids, active_id=inv_to_refund.id, active_model="account.invoice")
                .create({"description": "test refund", "date": inv_to_refund.date, "filter_refund": "cancel"})
            )
            refund_wizard.invoice_refund()

            # Create an invoice with a CABA tax, pay it, then unreconcile (this will create a CABA reverse move)
            inv_to_unrec = self.create_invoice(company, 100, test_tax, "2015-01-06", inv_line_account, pay=True)
            aml_to_unrec = inv_to_unrec.move_id.line_ids.filtered(
                lambda x: x.account_id.user_type_id.type in ("payable", "receivable")
            )
            aml_to_unrec.remove_move_reconcile()

        # Expected results in the tax report
        mig_check_data["tax_report_by_date"]["2015-01-01"] = {"03": 100, "54": 21, "81": 100, "59": 21}
        mig_check_data["tax_report_by_date"]["2015-01-02"] = {"49": 100, "64": 21, "81": -100, "85": 100, "63": 21}
        mig_check_data["tax_report_by_date"]["2015-01-03"] = {"03": 50, "54": 10.5, "81": 50, "59": 10.5}
        mig_check_data["tax_report_by_date"]["2015-01-04"] = {"49": 50, "64": 10.5, "81": -50, "85": 50, "63": 10.5}
        mig_check_data["tax_report_by_date"]["2015-01-05"] = {
            "03": 100,
            "54": 21,
            "59": 21,
            "49": 100,
            "64": 21,
            "85": 100,
            "63": 21,
        }
        mig_check_data["tax_report_by_date"]["2015-01-06"] = {
            "03": 100,
            "54": 21,
            "59": 21,
            "49": 100,
            "64": 21,
            "85": 100,
            "63": 21,
        }

        return mig_check_data

    def create_invoice(
        self, company, price_unit, tax, date, inv_line_account, refund=False, pay=False, negate_half=False
    ):
        """Returns an open invoice"""

        invoice_type = (tax.type_tax_use == "sale" and "out_" or "in_") + (refund and "refund" or "invoice")

        # account_type = "receivable" if tax.type_tax_use == "sale" else "payable"
        # rec_account_type = self.env.ref(f"account.data_account_type_{account_type}")
        # rec_account = self.env["account.account"].search(
        #     [("company_id", "=", company.id), ("user_type_id", "=", rec_account_type.id)], limit=1
        # )

        invoice_lines = [
            (
                0,
                0,
                {
                    "quantity": 1,
                    "price_unit": price_unit,
                    "name": "toto",
                    "account_id": inv_line_account.id,
                    "invoice_line_tax_ids": [(6, 0, [tax.id])],
                },
            )
        ]

        if negate_half:
            invoice_lines.append(
                (
                    0,
                    0,
                    {
                        "quantity": -1,
                        "price_unit": price_unit / 2,
                        "name": "toto",
                        "account_id": inv_line_account.id,
                        "invoice_line_tax_ids": [(6, 0, [tax.id])],
                    },
                )
            )

        partner = self.env["res.partner"].create(
            {
                "name": "Jean-Claude Dus",
            }
        )

        rslt = self.env["account.invoice"].create(
            {
                "partner_id": partner.id,
                "currency_id": self.env.ref("base.USD").id,
                "name": "invoice test rounding",
                #'account_id': rec_account.id,
                "type": invoice_type,
                "date": date,
                "company_id": company.id,
                "invoice_line_ids": invoice_lines,
            }
        )

        rslt._onchange_invoice_line_ids()
        rslt.action_invoice_open()

        if pay:
            bank_journal = self.env["account.journal"].search(
                [("type", "=", "bank"), ("company_id", "=", company.id)], limit=1
            )
            rslt.pay_and_reconcile(bank_journal, date=rslt.date)

        return rslt

    def check(self, init):
        company = self.env["res.company"].browse(init["company_id"])
        self.env.user.company_id = company

        for date, predicted_dict in init["tax_report_by_date"].items():
            report_opt = self.env["account.generic.tax.report"]._get_options(
                {
                    "date": {
                        "period_type": "custom",
                        "filter": "custom",
                        "date_to": date,
                        "mode": "range",
                        "date_from": date,
                    }
                }
            )
            new_context = self.env["account.generic.tax.report"]._set_context(report_opt)
            report_lines = self.env["account.generic.tax.report"].with_context(new_context)._get_lines(report_opt)
            report_dict = {line["id"]: line["columns"][0]["balance"] for line in report_lines}

            for tag_name, total in predicted_dict.items():
                report_line = self.env["account.tax.report.line"].search(
                    [("country_id", "=", company.country_id.id), ("tag_name", "=", tag_name)]
                )
                self.assertEqual(
                    total,
                    report_dict[report_line.id],
                    "Cash basis tax entry not migrated properply for tag_name %s, with case at date %s"
                    % (tag_name, date),
                )
