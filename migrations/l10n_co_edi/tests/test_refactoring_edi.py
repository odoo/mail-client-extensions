# -*- coding: utf-8 -*-
import base64
import datetime
from unittest.mock import patch

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.5")
class TestRefactoringEDI(UpgradeCase):
    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def _create_invoice_with_edi(self, user, invoice_vals):
        invoice = self.env["account.move"].with_user(user).create(invoice_vals)
        with patch(
            "odoo.addons.l10n_co_edi.models.account_invoice.AccountMove._l10n_co_edi_is_l10n_co_edi_required",
            return_value=False,
        ):
            invoice.action_post()
        xml_filename = invoice._l10n_co_edi_generate_electronic_invoice_filename()
        invoice.write(
            {
                "l10n_co_edi_datetime_invoice": datetime.datetime.now(),
                "l10n_co_edi_invoice_name": xml_filename,
                "l10n_co_edi_invoice_status": "accepted",
            }
        )
        xml = invoice.l10n_co_edi_generate_electronic_invoice_xml()

        attachment = (
            self.env["ir.attachment"]
            .with_user(user)
            .create(
                {
                    "name": xml_filename,
                    "res_id": invoice.id,
                    "res_model": invoice._name,
                    "datas": base64.encodebytes(xml),
                    "description": "Colombian invoice",
                }
            )
        )

        return invoice, attachment

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _create_invoice_posted_signed(self, user, invoice_vals):
        invoice, edi = self._create_invoice_with_edi(user, invoice_vals)
        invoice.l10n_co_edi_invoice_status = "accepted"
        return invoice.id, edi.id

    def _check_invoice_posted_signed(self, invoice, attachment_id):
        self.assertRecordValues(
            invoice,
            [
                {
                    "edi_state": "sent",
                }
            ],
        )
        document = invoice.edi_document_ids.filtered(lambda d: d.edi_format_id.code == "ubl_carvajal")
        self.assertRecordValues(
            document,
            [
                {
                    "state": "sent",
                    "attachment_id": attachment_id,
                }
            ],
        )

    def _create_invoice_posted_rejected(self, user, invoice_vals):
        invoice, edi = self._create_invoice_with_edi(user, invoice_vals)
        invoice.l10n_co_edi_invoice_status = "rejected"
        return invoice.id, edi.id

    def _check_invoice_posted_rejected(self, invoice, attachment_id):
        self.assertRecordValues(
            invoice,
            [
                {
                    "edi_state": "to_send",
                }
            ],
        )
        document = invoice.edi_document_ids.filtered(lambda d: d.edi_format_id.code == "ubl_carvajal")
        self.assertRecordValues(
            document,
            [
                {
                    "state": "to_send",
                    "blocking_level": "error",
                    "attachment_id": False,
                }
            ],
        )

    def _create_invoice_posted_processing(self, user, invoice_vals):
        invoice, edi = self._create_invoice_with_edi(user, invoice_vals)
        invoice.l10n_co_edi_invoice_status = "processing"
        invoice.l10n_co_edi_transaction = "test_transaction_id"
        return invoice.id, edi.id

    def _check_invoice_posted_processing(self, invoice, attachment_id):
        self.assertRecordValues(
            invoice,
            [
                {
                    "edi_state": "to_send",
                    "l10n_co_edi_transaction": "test_transaction_id",
                }
            ],
        )
        document = invoice.edi_document_ids.filtered(lambda d: d.edi_format_id.code == "ubl_carvajal")
        self.assertRecordValues(
            document,
            [
                {
                    "state": "to_send",
                    "attachment_id": False,
                }
            ],
        )

    def _create_invoice_posted_not_sent(self, user, invoice_vals):
        invoice, edi = self._create_invoice_with_edi(user, invoice_vals)
        invoice.l10n_co_edi_invoice_status = "not_sent"
        return invoice.id, edi.id

    def _check_invoice_posted_not_sent(self, invoice, attachment_id):
        self.assertRecordValues(
            invoice,
            [
                {
                    "edi_state": "to_send",
                }
            ],
        )
        document = invoice.edi_document_ids.filtered(lambda d: d.edi_format_id.code == "ubl_carvajal")
        self.assertRecordValues(
            document,
            [
                {
                    "state": "to_send",
                    "attachment_id": False,
                }
            ],
        )

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        company = self.env["res.company"].create({"name": "company for TestRefactoringEDI"})

        # Create user.
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "user TestRefactoringEDI",
                    "login": "TestRefactoringEDI",
                    "groups_id": [
                        (6, 0, self.env.user.groups_id.ids),
                        (4, self.env.ref("account.group_account_user").id),
                    ],
                    "company_ids": [(6, 0, company.ids)],
                    "company_id": company.id,
                }
            )
        )
        user.partner_id.email = "TestRefactoringEDI@test.com"

        chart_template = self.env.ref("l10n_co.l10n_co_chart_template_generic", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        if util.version_gte("saas~14.3"):
            chart_template.try_loading(company=company, install_demo=False)
        else:
            chart_template.try_loading(company=company)

        company.write(
            {
                "vat": "75101643",
                "street": "Av La Esperanza 3206",
                "city": "MEDELLÍN",
                "country_id": self.env.ref("base.co").id,
                "state_id": self.env.ref("base.state_co_01").id,
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
            [("company_id", "=", company.id), ("user_type_id.type", "=", "receivable")], limit=1
        )

        tax_16 = (
            self.env["account.tax"]
            .with_user(user)
            .create(
                {
                    "name": "tax_16",
                    "amount_type": "percent",
                    "amount": 16,
                    "type_tax_use": "sale",
                    "company_id": company.id,
                }
            )
        )

        product = (
            self.env["product.product"]
            .with_user(user)
            .create(
                {
                    "name": "product_co",
                    "weight": 2,
                    "uom_po_id": self.env.ref("uom.product_uom_kgm").id,
                    "uom_id": self.env.ref("uom.product_uom_kgm").id,
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
                    "name": "partner_co",
                    "property_account_receivable_id": account_receivable.id,
                    "l10n_co_edi_obligation_type_ids": [(6, 0, self.env.ref("l10n_co_edi.obligation_type_37").ids)],
                    "company_id": False,
                    "country_id": self.env.ref("base.co").id,
                    "state_id": self.env.ref("base.state_us_23").id,
                    "zip": 39301,
                    "vat": "CO213123432-1",
                }
            )
        )

        journal = (
            self.env["account.journal"]
            .with_user(user)
            .create(
                {
                    "name": "journal_co",
                    "code": "test_CO",
                    "type": "sale",
                    "company_id": company.id,
                    "l10n_co_edi_dian_authorization_number": "test_dian_number",
                }
            )
        )

        type_field = "move_type" if util.version_gte("saas~13.3") else "type"
        invoice_vals = {
            type_field: "out_invoice",
            "partner_id": partner.id,
            "invoice_date": "2017-01-01",
            "date": "2017-01-01",
            "invoice_incoterm_id": self.env.ref("account.incoterm_FCA").id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "price_unit": 2000.0,
                        "quantity": 1,
                        "tax_ids": [(6, 0, tax_16.ids)],
                    },
                )
            ],
            "journal_id": journal.id,
        }
        return [
            self._create_invoice_posted_signed(user, dict(invoice_vals)),
            self._create_invoice_posted_rejected(user, dict(invoice_vals)),
            self._create_invoice_posted_processing(user, dict(invoice_vals)),
            self._create_invoice_posted_not_sent(user, dict(invoice_vals)),
        ]

    def check(self, init):
        inv_id0, edi_id0 = init[0]
        inv_id1, edi_id1 = init[1]
        inv_id2, edi_id2 = init[2]
        inv_id3, edi_id3 = init[3]
        moves = self.env["account.move"].browse([inv_id0, inv_id1, inv_id2, inv_id3])
        partner = moves.partner_id

        self._check_invoice_posted_signed(moves[0], edi_id0)
        self._check_invoice_posted_rejected(moves[1], edi_id1)
        self._check_invoice_posted_processing(moves[2], edi_id2)
        self._check_invoice_posted_not_sent(moves[3], edi_id3)

        # Check removed values for l10n_co_edi_obligation_type_ids changed to default value
        self.assertEqual(partner.l10n_co_edi_obligation_type_ids.name, "R-99-PN")
