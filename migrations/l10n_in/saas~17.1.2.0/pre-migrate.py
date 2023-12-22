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
