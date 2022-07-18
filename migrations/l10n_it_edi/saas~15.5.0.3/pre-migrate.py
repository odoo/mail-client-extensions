# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "fetchmail.server", "l10n_it_last_uid")
    util.remove_field(cr, "fetchmail.server", "l10n_it_is_pec")
    util.remove_field(cr, "account.move", "l10n_it_send_state")
    util.remove_field(cr, "res.company", "l10n_it_address_send_fatturapa")
    util.remove_field(cr, "res.company", "l10n_it_address_recipient_fatturapa")
    util.remove_field(cr, "res.company", "l10n_it_mail_pec_server_id")

    util.remove_view(cr, "l10n_it_edi.fetchmail_server_form_l10n_it")
    util.remove_view(cr, "l10n_it_edi.invoice_supplier_tree_l10n_it")
    util.remove_view(cr, "l10n_it_edi.invoice_kanban_l10n_it")
    util.remove_view(cr, "l10n_it_edi.view_account_invoice_filter_l10n_it")
    util.remove_view(cr, "l10n_it_edi.res_company_form_l10n_it_inherit")
