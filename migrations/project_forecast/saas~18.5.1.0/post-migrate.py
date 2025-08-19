from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "project_forecast.planning_slot_template_rule_user")
