from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT id FROM resource_calendar WHERE hours_per_week IS NULL")
    to_compute_ids = [row[0] for row in cr.fetchall()]
    util.recompute_fields(cr, "resource.calendar", ["hours_per_week"], ids=to_compute_ids)
