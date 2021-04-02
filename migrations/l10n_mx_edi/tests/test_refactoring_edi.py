# -*- coding: utf-8 -*-
import base64
import os

from odoo.tools import misc

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


def coalesce(obj, *attrs):
    for attr in attrs:
        if hasattr(obj, attr):
            return getattr(obj, attr)
    raise AttributeError()


@change_version("13.5")
class TestRefactoringEDI(UpgradeCase):

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def _post_no_web_services(self, invoice):
        invoice.company_id.country_id = False
        invoice.post()
        invoice.company_id.country_id = self.env.ref("base.mx")

    def _create_invoice_with_cfdi(self, user, invoice_vals):
        invoice = self.env["account.move"].with_user(user).create(invoice_vals)
        self._post_no_web_services(invoice)

        render = coalesce(self.env["ir.qweb"], "render", "_render")
        cfdi_str = render(self.env.ref("l10n_mx_edi.cfdiv33"), invoice._l10n_mx_edi_create_cfdi_values())
        cfdi_str = cfdi_str.replace(b"xmlns__", b"xmlns:")
        filename = ("%s-%s-MX-Invoice-3-3.xml" % (invoice.journal_id.code, invoice.name)).replace("/", "")
        invoice.l10n_mx_edi_cfdi_name = filename

        cfdi = (
            self.env["ir.attachment"]
            .with_user(user)
            .create(
                {
                    "name": filename,
                    "res_id": invoice.id,
                    "res_model": invoice._name,
                    "datas": base64.encodebytes(cfdi_str),
                    "description": "Mexican invoice",
                }
            )
        )
        return invoice, cfdi

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _create_invoice_posted_signed_cfdi(self, user, invoice_vals):
        invoice, cfdi = self._create_invoice_with_cfdi(user, invoice_vals)
        invoice.l10n_mx_edi_pac_status = "signed"
        return invoice.id, cfdi.id

    def _check_invoice_posted_signed_cfdi(self, invoice, cfdi_id, mx_edi_format_id):
        self.assertRecordValues(
            invoice,
            [
                {
                    "edi_state": "sent",
                }
            ],
        )
        self.assertRecordValues(
            invoice.edi_document_ids,
            [
                {
                    "state": "sent",
                    "attachment_id": cfdi_id,
                    "edi_format_id": mx_edi_format_id,
                }
            ],
        )

    def _create_invoice_posted_not_signed_cfdi(self, user, invoice_vals):
        invoice, cfdi = self._create_invoice_with_cfdi(user, invoice_vals)
        invoice.l10n_mx_edi_pac_status = "retry"
        return invoice.id, cfdi.id

    def _check_invoice_posted_not_signed_cfdi(self, invoice, cfdi_id, mx_edi_format_id):
        self.assertRecordValues(
            invoice,
            [
                {
                    "edi_state": "to_send",
                }
            ],
        )
        self.assertRecordValues(
            invoice.edi_document_ids,
            [
                {
                    "state": "to_send",
                    "attachment_id": False,
                    "edi_format_id": mx_edi_format_id,
                }
            ],
        )

    def _create_invoice_posted_signed_multiple_cfdi(self, user, invoice_vals):
        invoice, cfdi_1 = self._create_invoice_with_cfdi(user, invoice_vals)
        invoice.l10n_mx_edi_pac_status = "signed"

        cfdi_2 = cfdi_1.copy()
        cfdi_3 = cfdi_2.copy()

        return invoice.id, cfdi_3.id

    def _check_invoice_posted_signed_multiple_cfdi(self, invoice, cfdi_id, mx_edi_format_id):
        self.assertRecordValues(invoice, [{"edi_state": "sent"}])
        self.assertRecordValues(
            invoice.edi_document_ids,
            [
                {
                    "state": "sent",
                    "attachment_id": cfdi_id,
                    "edi_format_id": mx_edi_format_id,
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

        chart_template = self.env.ref("l10n_mx.mx_coa", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading(company=company)

        certificate = self.env["l10n_mx_edi.certificate"].create(
            {
                "content": base64.encodebytes(
                    misc.file_open(
                        os.path.join("l10n_mx_edi", "demo", "pac_credentials", "certificate.cer"), "rb"
                    ).read()
                ),
                "key": base64.encodebytes(
                    misc.file_open(
                        os.path.join("l10n_mx_edi", "demo", "pac_credentials", "certificate.key"), "rb"
                    ).read()
                ),
                "password": "12345678a",
            }
        )
        certificate.write(
            {
                "date_start": "2016-01-01 01:00:00",
                "date_end": "2018-01-01 01:00:00",
            }
        )

        company.write(
            {
                "vat": "MXEKU9003173C9",
                "street_name": "Campobasso Norte",
                "street2": "Fraccionamiento Montecarlo",
                "street_number": "3206",
                "street_number2": "9000",
                "zip": "85134",
                "city": "Ciudad Obregón",
                "country_id": self.env.ref("base.mx").id,
                "state_id": self.env.ref("base.state_mx_son").id,
                "l10n_mx_edi_pac": "solfact",
                "l10n_mx_edi_pac_test_env": True,
                "l10n_mx_edi_fiscal_regime": "601",
                "l10n_mx_edi_certificate_ids": [(6, 0, certificate.ids)],
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
                    "l10n_mx_cfdi_tax_type": "Tasa",
                    "company_id": company.id,
                }
            )
        )

        product = (
            self.env["product.product"]
            .with_user(user)
            .create(
                {
                    "name": "product_mx",
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
                    "name": "partner_mx",
                    "property_account_receivable_id": account_receivable.id,
                    "company_id": False,
                    "country_id": self.env.ref("base.us").id,
                    "state_id": self.env.ref("base.state_us_23").id,
                    "zip": 39301,
                    "vat": "123456789",
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
        }

        return [
            self._create_invoice_posted_signed_cfdi(user, dict(invoice_vals)),
            self._create_invoice_posted_not_signed_cfdi(user, dict(invoice_vals)),
            self._create_invoice_posted_signed_multiple_cfdi(user, dict(invoice_vals)),
        ]

    def check(self, init):
        inv_id0, cfdi_id0 = init[0]
        inv_id1, cfdi_id1 = init[1]
        inv_id2, cfdi_id2 = init[2]
        moves = self.env["account.move"].browse([inv_id0, inv_id1, inv_id2])

        mx_edi_format_id = util.ref(self.env.cr, "l10n_mx_edi.edi_cfdi_3_3")
        self._check_invoice_posted_signed_cfdi(moves[0], cfdi_id0, mx_edi_format_id)
        self._check_invoice_posted_not_signed_cfdi(moves[1], cfdi_id1, mx_edi_format_id)
        self._check_invoice_posted_signed_multiple_cfdi(moves[2], cfdi_id2, mx_edi_format_id)
