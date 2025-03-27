from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.team", "opportunities_count")
    util.remove_field(cr, "crm.team", "opportunities_amount")
    util.remove_field(cr, "crm.team", "opportunities_overdue_count")
    util.remove_field(cr, "crm.team", "opportunities_overdue_amount")
