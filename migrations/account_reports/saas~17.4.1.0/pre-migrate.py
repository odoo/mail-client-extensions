from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, "account.report.footnote", "account.report.annotation")
    util.rename_field(cr, "account.report", "footnotes_ids", "annotations_ids")
    util.rename_xmlid(cr, *eb("account_reports.access_account_report_{footnote,annotation}_readonly"))
    util.rename_xmlid(cr, *eb("account_reports.access_account_report_{footnote,annotation}"))
    util.rename_xmlid(cr, *eb("account_reports.access_account_report_{footnote,annotation}_invoice"))

    # see https://github.com/odoo/enterprise/pull/65087
    util.explode_execute(
        cr,
        r"""
        UPDATE account_report_annotation
           SET line_id = regexp_replace(
               line_id,
               'groupby:([a-zA-Z0-9_]+)',
               '{{"groupby": "\1"}}',
               'g'
               )
         WHERE line_id LIKE '%groupby:%'
        """,
        table="account_report_annotation",
    )
