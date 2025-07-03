import base64
from datetime import date
from unittest.mock import patch

import requests
from dateutil.relativedelta import relativedelta

from odoo.tools import misc

from odoo.addons.base.maintenance.migrations.account.tests.test_common import (
    TestAccountingSetupCommon,
)
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~17.5")
class TestEdiDocumentToTbaiDocument(TestAccountingSetupCommon):
    def _mock_invoice_process_edi(self, invoice, blocking_level=None):
        with patch.object(
            type(self.env["account.edi.format"]),
            "_l10n_es_tbai_send_request_to_agency",
            return_value=None,
            side_effect=requests.RequestException("Connection error") if blocking_level == "warning" else None,
        ), patch.object(
            type(self.env["account.edi.format"]),
            "_l10n_es_tbai_process_post_response_bi",
            return_value=(True, "Success", None) if not blocking_level else (False, "Error", None),
        ):
            invoice.button_process_edi_web_services()

    def create_posted_invoice(self):
        invoice = (
            self.env["account.move"]
            .with_context(edi_test_mode=True)
            .create(
                {
                    "move_type": "out_invoice",
                    "partner_id": self.partner.id,
                    "invoice_line_ids": [(0, 0, {"product_id": self.product.id})],
                }
            )
        )
        invoice.action_post()

        return invoice

    def prepare(self):
        # Setup
        super().prepare(chart_template_ref="es_pymes")
        self.company.write(
            {
                "name": "EUS Company",
                "state_id": self.env.ref("base.state_es_ss").id,
                "country_id": self.env.ref("base.es").id,
                "vat": "ES09760433S",
                "l10n_es_edi_test_env": True,
            }
        )
        self.env["l10n_es_edi.certificate"].create(
            {
                "content": base64.encodebytes(
                    misc.file_open("l10n_es_edi_tbai/demo/certificates/Bizkaia-IZDesa2025.p12", "rb").read()
                ),
                "password": "IZDesa2025",
            }
        )
        self.company.l10n_es_tbai_tax_agency = "bizkaia"

        self.partner_es = self.env["res.partner"].create({"name": "Test partner", "vat": "ESF35999705"})
        self.product = self.env["product.product"].create({"name": "Test product", "lst_price": 100.0})

        moves_to_check = self.env["account.move"]

        # Invoice sent successfully
        invoice = self.create_posted_invoice()
        self._mock_invoice_process_edi(invoice)
        self.assertEqual(invoice.edi_state, "sent")
        self.assertTrue(invoice.l10n_es_tbai_chain_index)
        moves_to_check += invoice

        # Invoice sent failure
        invoice = self.create_posted_invoice()
        self._mock_invoice_process_edi(invoice, blocking_level="error")
        self.assertEqual(invoice.edi_state, "to_send")
        self.assertFalse(invoice.l10n_es_tbai_chain_index)
        moves_to_check += invoice

        # Invoice cancelled successfully
        invoice = self.create_posted_invoice()
        self._mock_invoice_process_edi(invoice)
        invoice.button_cancel_posted_moves()
        self.assertEqual(invoice.edi_state, "to_cancel")
        self._mock_invoice_process_edi(invoice)
        self.assertEqual(invoice.edi_state, "cancelled")
        moves_to_check += invoice

        # Invoice cancel failure
        invoice = self.create_posted_invoice()
        self._mock_invoice_process_edi(invoice)
        invoice.button_cancel_posted_moves()
        self._mock_invoice_process_edi(invoice, blocking_level="error")
        self.assertEqual(invoice.edi_state, "to_cancel")
        moves_to_check += invoice

        # Invoice sent pending
        invoice = self.create_posted_invoice()
        self._mock_invoice_process_edi(invoice, blocking_level="warning")
        self.assertEqual(invoice.edi_state, "to_send")
        self.assertTrue(invoice.l10n_es_tbai_chain_index)
        moves_to_check += invoice

        # Bill sent sucessfully
        bill = (
            self.env["account.move"]
            .with_context(edi_test_mode=True)
            .create(
                {
                    "move_type": "in_invoice",
                    "partner_id": self.partner.id,
                    "invoice_date": date.today() + relativedelta(days=1),
                    "invoice_line_ids": [(0, 0, {"product_id": self.product.id})],
                    "ref": "INV111",
                }
            )
        )
        bill.action_post()
        self._mock_invoice_process_edi(bill)
        self.assertEqual(bill.edi_state, "sent")
        self.assertFalse(bill.l10n_es_tbai_chain_index)
        moves_to_check += bill

        move_datas = moves_to_check.read(["id", "edi_state", "l10n_es_tbai_chain_index"])
        # 6 moves were created in this prepare function
        self.assertEqual(len(move_datas), 6)

        return {
            "move_datas": move_datas,
            "tbai_edi_format": self.env.ref("l10n_es_edi_tbai.edi_es_tbai").id,
        }

    def check(self, init):
        # EDI document to TBAI document
        for move_data in init["move_datas"]:
            move = self.env["account.move"].browse(move_data["id"])
            self.assertEqual(move.l10n_es_tbai_chain_index, move_data["l10n_es_tbai_chain_index"])
            self.assertFalse(move.edi_state)

            if move_data["edi_state"] == "to_send":
                self.assertEqual(move.l10n_es_tbai_state, "to_send")

                if not move_data["l10n_es_tbai_chain_index"]:
                    self.assertFalse(move.l10n_es_tbai_post_document_id)
                else:
                    self.assertTrue(move.l10n_es_tbai_post_document_id)
                    self.assertTrue(move.l10n_es_tbai_post_document_id.xml_attachment_id)

                self.assertFalse(move.l10n_es_tbai_cancel_document_id)

            elif move_data["edi_state"] in ("sent", "to_cancel"):
                self.assertEqual(move.l10n_es_tbai_state, "sent")
                self.assertTrue(move.l10n_es_tbai_post_document_id)
                self.assertTrue(move.l10n_es_tbai_post_document_id.xml_attachment_id)

            else:
                self.assertTrue(move.l10n_es_tbai_post_document_id)
                self.assertTrue(move.l10n_es_tbai_post_document_id.xml_attachment_id)
                self.assertTrue(move.l10n_es_tbai_cancel_document_id)
                self.assertTrue(move.l10n_es_tbai_cancel_document_id.xml_attachment_id)
                self.assertEqual(move.l10n_es_tbai_state, "cancelled")

        # No more account_edi_document for TBAI
        self.assertFalse(self.env["account.edi.document"].search([("edi_format_id", "=", init["tbai_edi_format"])]))
