from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_crm.res_partner_address_type")
