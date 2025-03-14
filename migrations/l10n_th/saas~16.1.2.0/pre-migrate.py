from odoo.upgrade import util


def migrate(cr, version):
    expr_to_line_xmlids = {
        "l10n_th.tax_report_vat_payable_balance": "l10n_th.tax_report_vat_payable",
        "l10n_th.tax_report_vat_excess_balance": "l10n_th.tax_report_vat_excess",
    }

    for expr_xmlid, line_xmlid in expr_to_line_xmlids.items():
        if util.ref(cr, expr_xmlid) is not None:
            continue

        line_id = util.ref(cr, line_xmlid)
        if line_id is None:
            continue

        util.ensure_xmlid_match_record(
            cr,
            expr_xmlid,
            "account.report.expression",
            {
                "report_line_id": line_id,
                "label": "balance",
            },
        )

        util.force_noupdate(cr, expr_xmlid, noupdate=False)
