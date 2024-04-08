from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "survey.question_result_summary_stat_numbers")
