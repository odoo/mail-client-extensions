from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_pine_labs.view_pos_pos_form_inherit_pos_pine_labs")
