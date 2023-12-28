# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_in.view_message_tree_audit_log")
    util.remove_view(cr, "l10n_in.view_message_tree_audit_log_search")
    util.remove_record(cr, "l10n_in.action_l10n_in_audit_trail_report")
    util.remove_record(cr, "l10n_in.l10n_in_audit_trail_report_menu")

    cr.execute(
        """
        UPDATE res_company company
           SET check_account_audit_trail = true
          FROM res_country country
         WHERE country.id = company.account_fiscal_country_id
           AND country.code = 'IN'
        """
    )

    util.remove_field(cr, "mail.message", "l10n_in_audit_log_preview")
    util.remove_field(cr, "mail.message", "l10n_in_audit_log_account_move_id")

    util.create_column(cr, "account_move_line", "l10n_in_hsn_code", "varchar")
    util.explode_execute(
        cr,
        """
        WITH lines AS (
           SELECT aml.id as line_id,
                  pt.l10n_in_hsn_code
             FROM account_move_line aml
             JOIN res_company c
               ON c.id = aml.company_id
             JOIN res_country co
               ON co.id = c.account_fiscal_country_id
             JOIN product_product p
               ON p.id = aml.product_id
             JOIN product_template pt
               ON pt.id = p.product_tmpl_id
            WHERE co.code = 'IN'
              AND pt.l10n_in_hsn_code IS NOT NULL
              AND {parallel_filter}
       )
       UPDATE account_move_line aml
          SET l10n_in_hsn_code = lines.l10n_in_hsn_code
         FROM lines
        WHERE lines.line_id = aml.id
        """,
        table="account_move_line",
        alias="aml",
    )
