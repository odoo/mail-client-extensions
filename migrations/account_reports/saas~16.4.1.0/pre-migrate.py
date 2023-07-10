# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    report_x_ref_map = {
        "aged_partner_balance": (
            util.ref(cr, "account_reports.aged_payable_report"),
            util.ref(cr, "account_reports.aged_receivable_report"),
        ),
        "partner_ledger": (util.ref(cr, "account_reports.partner_ledger_report"),),
    }
    for report, refs in report_x_ref_map.items():
        cr.execute(
            """
            WITH icp AS (
               DELETE FROM ir_config_parameter
                     WHERE key = %s
                 RETURNING value::NUMERIC AS threshold
            )
            UPDATE account_report ar
               SET prefix_groups_threshold = icp.threshold
              FROM icp
             WHERE ar.id IN %s
        """,
            [f"account_reports.{report}.groupby_prefix_groups_threshold", refs],
        )

    util.remove_model(cr, "account.bank.reconciliation.report.handler")
    util.remove_record(cr, "account_reports.action_account_report_bank_reconciliation")
    util.remove_record(cr, "account_reports.bank_reconciliation_report")
