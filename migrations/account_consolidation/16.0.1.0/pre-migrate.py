from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "account.consolidation.trial_balance_report")

    for view_xml_id in (
        "header_cell_template",
        "line_template",
        "search_template_conso_extra_options",
        "search_template_consolidation_period_comparisons",
        "search_template_consolidation_journals",
        "search_template",
        "main_template_conso_report",
    ):
        util.remove_view(cr, f"account_consolidation.{view_xml_id}")
