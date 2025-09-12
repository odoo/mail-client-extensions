from odoo.upgrade import util


def migrate(cr, version):
    query = "SELECT id FROM resource_calendar WHERE hours_per_week IS NULL"
    util.recompute_fields(cr, "resource.calendar", ["hours_per_week"], query=query)
