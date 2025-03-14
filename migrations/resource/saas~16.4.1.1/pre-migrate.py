from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "resource.resource_calendar_std_35h", "resource.resource_calendar_std_38h")
