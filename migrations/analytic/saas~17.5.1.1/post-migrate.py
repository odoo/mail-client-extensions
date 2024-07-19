from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "analytic.analytic_plan_projects", util.update_record_from_xml)
