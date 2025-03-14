from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.workorder", "is_expired")

    util.remove_view(cr, "mrp_workorder_expiry.mrp_workorder_view_form_tablet_inherit_expiry")
