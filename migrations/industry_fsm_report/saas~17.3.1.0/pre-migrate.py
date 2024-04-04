from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "industry_fsm_report.worksheet_template_view_form_no_design_button",
        "industry_fsm_report.worksheet_template_view_form_footer_design_button",
    )
