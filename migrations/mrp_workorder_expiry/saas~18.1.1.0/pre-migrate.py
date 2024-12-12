from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_workorder_expiry.quality_check_view_form_tablet_inherit_expiry")
