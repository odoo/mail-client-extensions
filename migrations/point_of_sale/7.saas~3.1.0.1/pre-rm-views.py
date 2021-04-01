from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "point_of_sale.view_report_pos_order_tree")
