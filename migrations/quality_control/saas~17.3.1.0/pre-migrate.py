from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "quality_control.action_qualtity_alert", "quality_control.stock_picking_action_quality_alert")
