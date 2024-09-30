from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "calendar.event", "on_leave_partner_ids")
