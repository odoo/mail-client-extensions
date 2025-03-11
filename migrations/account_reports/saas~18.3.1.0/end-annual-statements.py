from odoo.upgrade import util


def migrate(cr, version):
    if root_annual_statements_id := util.ref(cr, "account_reports.annual_statements"):
        AccountReport = util.env(cr)["account.report"]
        root_annual_statements = AccountReport.browse(root_annual_statements_id)
        asr_section_report_ids = AccountReport.search(AccountReport._asr_sections_domain(root_annual_statements)).ids
        util.iter_browse(AccountReport, asr_section_report_ids)._link_annual_statements(root_annual_statements)
