from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "purchase.requisition", "procurement_group_id")
