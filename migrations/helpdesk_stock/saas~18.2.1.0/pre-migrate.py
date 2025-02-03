from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_stock.helpdesk_ticket_view_tree_inherit_helpdesk_stock")
