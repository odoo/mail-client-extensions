from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "quality.point", "failure_location_ids", "quality_control", "quality")
    util.move_field_to_module(cr, "quality.check", "failure_location_id", "quality_control", "quality")
