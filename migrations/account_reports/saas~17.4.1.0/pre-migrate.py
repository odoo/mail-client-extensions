from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, "account.report.footnote", "account.report.annotation")
    util.rename_field(cr, "account.report", "footnotes_ids", "annotations_ids")
    util.rename_xmlid(cr, *eb("account_reports.access_account_report_{footnote,annotation}_readonly"))
    util.rename_xmlid(cr, *eb("account_reports.access_account_report_{footnote,annotation}"))
    util.rename_xmlid(cr, *eb("account_reports.access_account_report_{footnote,annotation}_invoice"))
