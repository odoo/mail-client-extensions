# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Convert the old Many2one device to report fields to Many2many fields
    util.create_m2m(cr, "iot_device_ir_act_report_xml_rel", "iot_device", "ir_act_report_xml")
    query = """
        INSERT INTO iot_device_ir_act_report_xml_rel (iot_device_id, ir_act_report_xml_id)
        SELECT device_id, id FROM ir_act_report_xml WHERE device_id IS NOT NULL
    """
    cr.execute(query)
    util.remove_field(cr, "ir.actions.report", "device_id")
