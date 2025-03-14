from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "survey.certification_report_view_classic")
    util.remove_view(cr, "survey.certification_report_view_modern")

    util.create_column(cr, "survey_survey", "survey_type", "varchar", default="custom")
