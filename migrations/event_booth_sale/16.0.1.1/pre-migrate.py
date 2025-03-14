from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Now uses event_booth_view_tree_from_event
    util.remove_view(cr, "event_booth_sale.event_booth_view_tree")
