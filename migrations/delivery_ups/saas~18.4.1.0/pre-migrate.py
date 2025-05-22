from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "delivery_ups.view_picking_withcarrier_out_form_inherit_delivery_ups")
