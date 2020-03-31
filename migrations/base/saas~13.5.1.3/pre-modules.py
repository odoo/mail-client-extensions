# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_module(cr, "pos_reprint")

    if util.has_enterprise():
        util.merge_module(cr, "iot_pairing", "iot")

        util.merge_module(cr, 'l10n_co_edi_ubl_2_1', 'l10n_co_edi')
        util.module_deps_diff(cr, 'l10n_co_edi', plus={'product_unspsc'})

    util.module_deps_diff(cr, 'l10n_co', plus={'base_address_city', 'account_debit_note', 'l10n_latam_base'})

    util.create_column(cr, 'res_country', 'zip_required', 'boolean', default=True)
    util.create_column(cr, 'res_country', 'state_required', 'boolean', default=False)
    util.new_module(cr, "microsoft_account", deps={"base_setup"})
    util.new_module(cr, "microsoft_calendar", deps={"microsoft_account", "calendar"})

    util.rename_xmlid(cr, *eb('base.module_category_{localization,accounting_localizations}_account_charts'))
    util.remove_record(cr, 'base.module_category_localization')
    util.remove_record(cr, 'base.module_category_operations')

    util.remove_module(cr, 'hr_expense_check')
    util.remove_module(cr, 'website_project')

    util.module_deps_diff(cr, "l10n_ec", plus={"l10n_latam_invoice_document", "l10n_latam_base"})

    if util.has_enterprise():
        util.module_deps_diff(cr, 'l10n_ar_edi', minus={'account_debit_note'})

    util.module_deps_diff(cr, 'l10n_latam_invoice_document', plus={'account_debit_note'})
