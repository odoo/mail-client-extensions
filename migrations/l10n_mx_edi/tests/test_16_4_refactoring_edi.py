# -*- coding: utf-8 -*-
import base64
from unittest.mock import patch

from freezegun import freeze_time
from lxml import etree

from odoo.tools import misc

from odoo.addons.base.maintenance.migrations.account.tests.test_common import (
    TestAccountingSetupCommon,
)
from odoo.addons.base.maintenance.migrations.testing import change_version


class TestRefactoringL10nMxEDI(TestAccountingSetupCommon, abstract=True):
    def with_mocked_pac_method(self, method_name, method_replacement):
        """Helper to mock an rpc call to the PAC.
        :param method_name:         The name of the method to mock.
        :param method_replacement:  The method to be called instead.
        """
        return patch.object(type(self.env["account.edi.format"]), method_name, method_replacement)

    def prepare(self):
        results = super().prepare(chart_template_ref="mx")

        self.certificate = self.env["l10n_mx_edi.certificate"].create(
            {
                "content": base64.encodebytes(
                    misc.file_open("l10n_mx_edi/demo/pac_credentials/certificate.cer", "rb").read()
                ),
                "key": base64.encodebytes(
                    misc.file_open("l10n_mx_edi/demo/pac_credentials/certificate.key", "rb").read()
                ),
                "password": "12345678a",
            }
        )
        self.certificate.write(
            {
                "date_start": "2016-01-01 01:00:00",
                "date_end": "2018-01-01 01:00:00",
            }
        )

        self.env.company.write(
            {
                "vat": "EKU9003173C9",
                "street": "Campobasso Norte 3206 - 9000",
                "street2": "Fraccionamiento Montecarlo",
                "zip": "85134",
                "city": "Ciudad Obregón",
                "country_id": self.env.ref("base.mx").id,
                "state_id": self.env.ref("base.state_mx_son").id,
                "l10n_mx_edi_pac": "solfact",
                "l10n_mx_edi_pac_test_env": True,
                "l10n_mx_edi_fiscal_regime": "601",
                "l10n_mx_edi_certificate_ids": [(6, 0, self.certificate.ids)],
            }
        )

        self.product = self.env["product.product"].create(
            {
                "name": "product_mx",
                "default_code": "product_mx",
                "uom_po_id": self.env.ref("uom.product_uom_kgm").id,
                "uom_id": self.env.ref("uom.product_uom_kgm").id,
                "lst_price": 1000.0,
                "property_account_income_id": self.account_income.id,
                "unspsc_code_id": self.env.ref("product_unspsc.unspsc_code_01010101").id,
            }
        )
        return results


@change_version("saas~16.4")
class TestRefactoringEDI(TestRefactoringL10nMxEDI):
    def with_mocked_pac_sign_success(self, method_name):
        """Fake the SAT cfdi stamping."""

        def method_replacement(_format, _record, exported):
            # Inject UUID.
            tree = etree.fromstring(exported["cfdi_str"])
            uuid = f"00000000-0000-0000-0000-{tree.attrib['Folio'].rjust(12, '0')}"
            stamp = f"""
                <tfd:TimbreFiscalDigital
                    xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
                    xsi:schemaLocation="http://www.sat.gob.mx/TimbreFiscalDigital http://www.sat.gob.mx/sitio_internet/cfd/TimbreFiscalDigital/TimbreFiscalDigitalv11.xsd"
                    Version="1.1"
                    UUID="{uuid}"
                    FechaTimbrado="___ignore___"
                    RfcProvCertif="___ignore___"
                    SelloCFD="___ignore___"/>
            """
            complemento_node = tree.xpath("//*[local-name()='Complemento']")
            if complemento_node:
                complemento_node[0].insert(len(tree), etree.fromstring(stamp))
            else:
                complemento_node = f"""
                    <cfdi:Complemento
                        xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xsi:schemaLocation="http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd">
                        {stamp}
                    </cfdi:Complemento>
                """
                tree.insert(len(tree), etree.fromstring(complemento_node))
                tree[-1].attrib.clear()
            cfdi_str = etree.tostring(tree, xml_declaration=True, encoding="UTF-8")

            return {
                "cfdi_signed": cfdi_str,
                "cfdi_encoding": "str",
            }

        return self.with_mocked_pac_method(method_name, method_replacement)

    def with_mocked_pac_invoice_sign_success(self):
        return self.with_mocked_pac_sign_success("_l10n_mx_edi_post_invoice_pac")

    def with_mocked_pac_payment_sign_success(self):
        return self.with_mocked_pac_sign_success("_l10n_mx_edi_post_payment_pac")

    @freeze_time("2017-01-01")
    def _prepare_test_invoice_with_payment(self):
        inv = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2017-01-01",
                "date": "2017-01-01",
                "invoice_date_due": "2017-02-01",  # Force PPD by default
                "l10n_mx_edi_payment_method_id": self.env.ref("l10n_mx_edi.payment_method_efectivo").id,
                "invoice_line_ids": [(0, 0, {"product_id": self.product.id})],
            }
        )
        with self.with_mocked_pac_invoice_sign_success():
            inv.action_post()
            inv.edi_document_ids._process_documents_web_services(with_commit=False)
            inv.l10n_mx_edi_sat_status = "not_found"
        with self.with_mocked_pac_payment_sign_success():
            pay = (
                self.env["account.payment.register"]
                .with_context(active_model="account.move", active_ids=inv.ids)
                .create({})
                ._create_payments()
            )
            pay.edi_document_ids._process_documents_web_services(with_commit=False)
            pay.move_id.l10n_mx_edi_sat_status = "valid"

        # For some reason, this compute is not triggered at the right time in this setup.
        # Since it's a stored field, invalidating the value is not enough.
        pay.move_id._compute_l10n_mx_edi_cfdi_request()

        self.assertRecordValues(
            inv + pay.move_id,
            [
                {
                    "l10n_mx_edi_cfdi_request": "on_invoice",
                    "l10n_mx_edi_sat_status": "not_found",
                    "l10n_mx_edi_cfdi_uuid": "00000000-0000-0000-0000-000000000001",
                },
                {
                    "l10n_mx_edi_cfdi_request": "on_payment",
                    "l10n_mx_edi_sat_status": "valid",
                    "l10n_mx_edi_cfdi_uuid": "00000000-0000-0000-0000-000000000001",
                },
            ],
        )
        self.assertRecordValues(inv.edi_document_ids + pay.edi_document_ids, [{"state": "sent"}] * 2)
        self.assertTrue(inv.edi_document_ids.attachment_id)
        self.assertTrue(pay.edi_document_ids.attachment_id)

        return inv.id, pay.id, inv.edi_document_ids.attachment_id.id, pay.edi_document_ids.attachment_id.id

    def _check_invoice_with_payment(self, _config, inv_id, pay_id, inv_cfdi_id, pay_cfdi_id):
        inv = self.env["account.move"].browse(inv_id)
        pay = self.env["account.payment"].browse(pay_id)

        self.assertRecordValues(
            inv + pay.move_id,
            [
                {
                    "edi_state": False,
                    "l10n_mx_edi_is_cfdi_needed": True,
                    "l10n_mx_edi_cfdi_state": "sent",
                    "l10n_mx_edi_cfdi_sat_state": "not_found",
                    "l10n_mx_edi_cfdi_attachment_id": inv_cfdi_id,
                    "l10n_mx_edi_cfdi_uuid": "00000000-0000-0000-0000-000000000001",
                },
                {
                    "edi_state": False,
                    "l10n_mx_edi_is_cfdi_needed": True,
                    "l10n_mx_edi_cfdi_state": "sent",
                    "l10n_mx_edi_cfdi_sat_state": "valid",
                    "l10n_mx_edi_cfdi_attachment_id": pay_cfdi_id,
                    "l10n_mx_edi_cfdi_uuid": "00000000-0000-0000-0000-000000000001",
                },
            ],
        )
        self.assertRecordValues(
            inv.l10n_mx_edi_invoice_document_ids,
            [
                {
                    "invoice_ids": inv.ids,
                    "move_id": pay.move_id.id,
                    "attachment_id": pay_cfdi_id,
                    "state": "payment_sent",
                    "sat_state": "valid",
                },
                {
                    "invoice_ids": inv.ids,
                    "move_id": inv.id,
                    "attachment_id": inv_cfdi_id,
                    "state": "invoice_sent",
                    "sat_state": "not_found",
                },
            ],
        )

    def prepare(self):
        results = super().prepare()
        results["tests"].append(("_check_invoice_with_payment", self._prepare_test_invoice_with_payment()))
        return results
