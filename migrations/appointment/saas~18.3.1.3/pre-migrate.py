from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "calendar.event", "on_leave_partner_ids")
    util.rename_field(cr, "calendar.event", "on_leave_resource_ids", "unavailable_resource_ids")
