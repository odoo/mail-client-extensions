from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "hr.attendance", ["overtime_hours", "validated_overtime_hours"])
