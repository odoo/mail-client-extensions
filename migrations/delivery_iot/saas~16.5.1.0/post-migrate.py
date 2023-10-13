# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Save the (shipping label) printers assigned in the operation type to the report added after the module is updated
    cr.execute(
        """
            INSERT INTO iot_device_ir_act_report_xml_rel (iot_device_id, ir_act_report_xml_id)
            SELECT iot_printer_id, %s FROM stock_picking_type WHERE iot_printer_id IS NOT NULL
        """,
        [util.ref(cr, "delivery_iot.action_report_shipping_labels")],
    )
    util.remove_field(cr, "stock.picking.type", "iot_printer_id")
