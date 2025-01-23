from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.recruitment.stage.report", "unique_candidate")
    util.remove_field(cr, "hr.recruitment.report", "unique_candidate")
