from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_plm.mrp_eco_bom_change_view_form")
    util.remove_view(cr, "mrp_plm.mrp_eco_routing_change_view_form")
    util.remove_field(cr, "mrp.eco.routing.change", "old_time_cycle_manual")
    util.remove_field(cr, "mrp.eco.routing.change", "new_time_cycle_manual")
