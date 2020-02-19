# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    #removed fields
    util.remove_field(cr, 'account.move', 'l10n_in_partner_vat')
    util.remove_field(cr, 'l10n_in.account.invoice.report', 'l10n_in_export_type')
    util.remove_field(cr, 'res.partner', 'l10n_in_country_code')
    util.remove_field(cr, 'res.users', 'l10n_in_country_code')
    util.remove_field(cr, 'account.move', 'l10n_in_import_export')
    
    # create column in db for new fields in account_move table
    util.create_column(cr, "account_move", "l10n_in_gstin", "varchar")
    util.create_column(cr, "account_move", "l10n_in_state_id", "int4")
    util.create_column(cr, "account_move", "l10n_in_gst_treatment", "varchar")

    # create column in db for new fields in res_partner table
    util.create_column(cr, "res_partner", "l10n_in_gst_treatment", "varchar")
