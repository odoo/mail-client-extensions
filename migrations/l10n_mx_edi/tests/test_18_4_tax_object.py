import base64
import contextlib
from contextlib import contextmanager
from unittest.mock import patch

from freezegun import freeze_time
from lxml import etree

with contextlib.suppress(ImportError):
    from odoo import Command
from odoo.tools import misc

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.account.tests.test_common import (
    TestAccountingSetupCommon,
)
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~18.4")
class TestL10nMxEDITaxObject(TestAccountingSetupCommon):
    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    @contextmanager
    def with_mocked_pac_method(self, method_name, method_replacement):
        """Helper to mock an rpc call to the PAC.

        :param method_name:         The name of the method to mock.
        :param method_replacement:  The method to be called instead.
        """
        with patch.object(type(self.env["l10n_mx_edi.document"]), method_name, method_replacement):
            yield

    def with_mocked_pac_sign_success(self):
        """Fake the SAT cfdi stamping."""
        method_name = f"_{self.env.company.l10n_mx_edi_pac}_sign"

        def fake_success(_record, _credentials, cfdi_str):
            # Inject UUID.
            tree = etree.fromstring(cfdi_str)
            self.uuid += 1
            uuid = f"00000000-0000-0000-0000-{str(self.uuid).rjust(12, '0')}"
            stamp = f"""
                <tfd:TimbreFiscalDigital
                    xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
                    xsi:schemaLocation="http://www.sat.gob.mx/TimbreFiscalDigital http://www.sat.gob.mx/sitio_internet/cfd/TimbreFiscalDigital/TimbreFiscalDigitalv11.xsd"
                    Version="1.1"
                    UUID="{uuid}"
                    FechaTimbrado="___ignore___"
                    NoCertificadoSAT="___ignore___"
                    RfcProvCertif="___ignore___"
                    SelloCFD="___ignore___"
                    SelloSAT="___ignore___"
                />
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

            return {"cfdi_str": cfdi_str}

        return self.with_mocked_pac_method(method_name, fake_success)

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    @freeze_time("2018-01-01")
    def _prepare_test_invoiceable_partner_no_tax_breakdown(self):
        """Partner has "l10n_mx_edi_no_tax_breakdown" set to True and can be invoiced."""
        self.partner.l10n_mx_edi_no_tax_breakdown = True
        self.partner.type = "invoice"

        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "tax_ids": [Command.set(self.tax_16.ids)],
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "discount": 100.0,
                            "tax_ids": [Command.set(self.tax_16.ids)],
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "tax_ids": [],
                        }
                    ),
                ],
            },
        )
        invoice.action_post()
        with self.with_mocked_pac_sign_success():
            invoice._l10n_mx_edi_cfdi_invoice_try_send()
        self.assertRecordValues(invoice, [{"l10n_mx_edi_cfdi_state": "sent"}])
        return invoice.ids

    def _check_test_invoiceable_partner_no_tax_breakdown(self, config, invoice_id):
        self._check_tax_objects(config, invoice_id)

    @freeze_time("2018-01-01")
    def _prepare_test_fallback_commercial_partner_tax_breakdown(self):
        """The tax breakdown will be retrieve from the commercial partner who has "l10n_mx_edi_no_tax_breakdown" set to False."""
        partner_2 = self.partner.copy()
        partner_2.is_company = False
        partner_2.l10n_mx_edi_no_tax_breakdown = False
        partner_2.type = "contact"
        partner_3 = self.partner.copy()
        partner_3.l10n_mx_edi_no_tax_breakdown = True
        partner_3.type = "invoice"
        partner_2.commercial_partner_id = partner_3

        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner_2.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "tax_ids": [Command.set(self.tax_16.ids)],
                        }
                    ),
                ],
            },
        )
        invoice.action_post()
        with self.with_mocked_pac_sign_success():
            invoice._l10n_mx_edi_cfdi_invoice_try_send()
        self.assertRecordValues(invoice, [{"l10n_mx_edi_cfdi_state": "sent"}])
        return invoice.ids

    def _check_test_fallback_commercial_partner_tax_breakdown(self, config, invoice_id):
        return self._check_tax_objects(config, invoice_id)

    @freeze_time("2018-01-01")
    def _prepare_test_local_tax(self):
        self.partner.l10n_mx_edi_no_tax_breakdown = True
        self.partner.type = "invoice"

        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "tax_ids": [Command.set(self.local_tax_16_transferred.ids)],
                        }
                    ),
                ],
            },
        )
        invoice.action_post()
        with self.with_mocked_pac_sign_success():
            invoice._l10n_mx_edi_cfdi_invoice_try_send()
        self.assertRecordValues(invoice, [{"l10n_mx_edi_cfdi_state": "sent"}])
        return invoice.ids

    def _check_tax_objects(self, config, invoice_id):
        invoice = self.env["account.move"].browse(invoice_id)
        self.assertTrue(invoice.l10n_mx_edi_invoice_document_ids)
        tree = etree.fromstring(invoice.l10n_mx_edi_invoice_document_ids.attachment_id.raw)
        self.assertRecordValues(
            invoice.invoice_line_ids,
            [
                {"l10n_mx_edi_tax_object": concepto_node.attrib.get("ObjetoImp")}
                for concepto_node in tree.findall("{*}Conceptos/{*}Concepto")
            ],
        )

    def prepare(self):
        results = super().prepare(chart_template_ref="mx")

        if not util.version_gte("18.0"):
            return None

        key = self.env["certificate.key"].create(
            {
                "content": base64.encodebytes(
                    misc.file_open("l10n_mx_edi/demo/pac_credentials/certificate.key", "rb").read()
                ),
                "password": "12345678a",
                "company_id": self.company.id,
            }
        )
        self.certificate = self.env["certificate.certificate"].create(
            {
                "content": base64.encodebytes(
                    misc.file_open("l10n_mx_edi/demo/pac_credentials/certificate.cer", "rb").read()
                ),
                "private_key_id": key.id,
                "company_id": self.company.id,
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
                "l10n_mx_edi_certificate_ids": [Command.set(self.certificate.ids)],
            }
        )
        self.uuid = 0

        self.tax_16 = self.env["account.chart.template"].ref("tax12")
        self.local_tax_group = self.env["account.tax.group"].create({"name": "Local VAT"})
        self.local_tax_16_transferred = self.tax_16.copy(
            default={
                "name": "local 16%",
                "tax_group_id": self.local_tax_group.id,
            }
        )

        self.product = self.env["product.product"].create(
            {
                "name": "product_mx",
                "default_code": "product_mx",
                "uom_id": self.env.ref("uom.product_uom_kgm").id,
                "lst_price": 1000.0,
                "property_account_income_id": self.account_income.id,
                "unspsc_code_id": self.env.ref("product_unspsc.unspsc_code_01010101").id,
            }
        )

        results["tests"].append(
            (
                "_check_test_invoiceable_partner_no_tax_breakdown",
                self._prepare_test_invoiceable_partner_no_tax_breakdown(),
            )
        )
        results["tests"].append(
            (
                "_check_test_fallback_commercial_partner_tax_breakdown",
                self._prepare_test_fallback_commercial_partner_tax_breakdown(),
            )
        )
        results["tests"].append(("_check_tax_objects", self._prepare_test_local_tax()))
        return results
