from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_workorder_iot.quality_check_view_form_iot_inherit_quality")
