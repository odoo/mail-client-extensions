from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "quality_mrp_workorder_iot.mrp_workorder_view_form_iot_inherit")
