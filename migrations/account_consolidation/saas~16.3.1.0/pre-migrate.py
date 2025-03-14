from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_consolidation.line_template_consolidation_report")
    util.remove_view(cr, "account_consolidation.cell_template_consolidation_report")
    util.remove_view(cr, "account_consolidation.main_table_header_template_consolidation_report")
    util.remove_view(cr, "account_consolidation.main_template_consolidation_report")
    util.remove_view(cr, "account_consolidation.search_template_consolidation_report_extra_options")
    util.remove_view(cr, "account_consolidation.search_template_consolidation_report_journals")
    util.remove_view(cr, "account_consolidation.search_template_consolidation_report_period_comparisons")
    util.remove_view(cr, "account_consolidation.search_template_consolidation_report")
