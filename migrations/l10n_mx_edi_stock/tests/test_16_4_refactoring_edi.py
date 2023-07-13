# -*- coding: utf-8 -*-
from freezegun import freeze_time
from lxml import etree

from odoo.addons.base.maintenance.migrations.l10n_mx_edi.tests.test_16_4_refactoring_edi import TestRefactoringL10nMxEDI
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version('saas~16.4')
class TestRefactoringEDI(TestRefactoringL10nMxEDI):

    def with_mocked_pac_sign_success(self):
        """ Fake the SAT cfdi stamping. """

        def method_replacement(_format, credentials, cfdi):
            # Inject UUID.
            tree = etree.fromstring(cfdi)
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
            cfdi_str = etree.tostring(tree, xml_declaration=True, encoding='UTF-8')

            return {
                'cfdi_signed': cfdi_str,
                'cfdi_encoding': 'str',
            }

        return self.with_mocked_pac_method('_l10n_mx_edi_solfact_sign', method_replacement)

    @freeze_time('2017-01-01')
    def _prepare_test_stock_picking(self):
        picking = self.env['stock.picking'].create({
            'location_id': self.new_wh.lot_stock_id.id,
            'location_dest_id': self.customer_location.id,
            'picking_type_id': self.new_wh.out_type_id.id,
            'partner_id': self.partner.id,
            'l10n_mx_edi_transport_type': '01',
            'l10n_mx_edi_vehicle_id': self.vehicle_pedro.id,
            'l10n_mx_edi_distance': 120,
            'state': 'draft',
            'immediate_transfer': False,
        })
        self.env['stock.move'].create({
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom_qty': 10,
            'product_uom': self.product.uom_id.id,
            'picking_id': picking.id,
            'location_id': self.new_wh.lot_stock_id.id,
            'location_dest_id': self.customer_location.id,
            'state': 'confirmed',
            'description_picking': self.product.name,
        })

        self.env['stock.quant']._update_available_quantity(self.product, self.new_wh.lot_stock_id, 10.0)
        picking.action_assign()
        picking.move_ids[0].move_line_ids[0].qty_done = 10
        picking._action_done()

        with self.with_mocked_pac_sign_success():
            picking.l10n_mx_edi_action_send_delivery_guide()
            picking.l10n_mx_edi_sat_status = 'valid'

        self.assertRecordValues(picking, [{
            'l10n_mx_edi_status': 'sent',
            'l10n_mx_edi_sat_status': 'valid',
        }])
        self.assertTrue(picking.l10n_mx_edi_cfdi_file_id)

        return picking.id, picking.l10n_mx_edi_cfdi_file_id.id

    def _check_stock_picking(self, _config, picking_id, cfdi_id):
        picking = self.env['stock.picking'].browse(picking_id)
        self.assertRecordValues(picking, [{
            'l10n_mx_edi_is_cfdi_needed': True,
            'l10n_mx_edi_cfdi_state': 'sent',
            'l10n_mx_edi_cfdi_sat_state': 'valid',
            'l10n_mx_edi_cfdi_attachment_id': cfdi_id,
            'l10n_mx_edi_cfdi_uuid': '00000000-0000-0000-0000-000000000001',
        }])
        self.assertRecordValues(picking.l10n_mx_edi_document_ids, [
            {
                'picking_id': picking_id,
                'attachment_id': cfdi_id,
                'state': 'picking_sent',
                'sat_state': 'valid',
            },
        ])

    def prepare(self):
        results = super().prepare()

        self.new_wh = self.env['stock.warehouse'].create({
            'name': 'New Warehouse',
            'reception_steps': 'one_step',
            'delivery_steps': 'ship_only',
            'code': 'NWH'
        })

        self.customer_location = self.env.ref('stock.stock_location_customers')

        self.product.write({
            'type': 'product',
            'unspsc_code_id': self.env.ref('product_unspsc.unspsc_code_56101500').id,
            'weight': 1,
        })

        self.partner = self.env['res.partner'].create({
            'name': 'INMOBILIARIA',
            'street': 'Street Calle',
            'city': 'Hidalgo del Parral',
            'country_id': self.env.ref('base.mx').id,
            'state_id': self.env.ref('base.state_mx_chih').id,
            'zip': '33826',
            'vat': 'ICV060329BY0',
        })

        self.operator_pedro = self.env['res.partner'].create({
            'name': 'Amigo Pedro',
            'vat': 'VAAM130719H60',
            'street': 'JESUS VALDES SANCHEZ',
            'city': 'Arteaga',
            'country_id': self.env.ref('base.mx').id,
            'state_id': self.env.ref('base.state_mx_coah').id,
            'zip': '25350',
            'l10n_mx_edi_operator_licence': 'a234567890',
        })

        self.vehicle_pedro = self.env['l10n_mx_edi.vehicle'].create({
            'name': 'DEMOPERMIT',
            'transport_insurer': 'DEMO INSURER',
            'transport_insurance_policy': 'DEMO POLICY',
            'transport_perm_sct': 'TPAF10',
            'vehicle_model': '2020',
            'vehicle_config': 'T3S1',
            'vehicle_licence': 'ABC123',
            'trailer_ids': [(0, 0, {'name': 'trail1', 'sub_type': 'CTR003'})],
            'figure_ids': [
                (0, 0, {
                    'type': '01',
                    'operator_id': self.operator_pedro.id,
                }),
                (0, 0, {
                    'type': '02',
                    'operator_id': self.env.company.partner_id.id,
                    'part_ids': [(6, 0, self.env.ref('l10n_mx_edi_stock.l10n_mx_edi_part_05').ids)],
                }),
            ],
        })

        results["tests"].append(('_check_stock_picking', self._prepare_test_stock_picking()))
        return results
