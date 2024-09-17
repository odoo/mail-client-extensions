from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "membership.view_partner_tree")
