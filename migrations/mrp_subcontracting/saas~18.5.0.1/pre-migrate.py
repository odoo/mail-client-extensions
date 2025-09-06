from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking", "display_action_record_components")
    util.remove_field(cr, "stock.location", "is_subcontracting_location")
    util.remove_view(cr, "mrp_subcontracting.view_location_form")
