from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "purchase.requisition.create.alternative", "partner_id")
