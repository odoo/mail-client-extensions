# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_module(cr, "pos_reprint")

    if util.has_enterprise():
        util.merge_module(cr, "iot_pairing", "iot")

    util.create_column(cr, 'res_country', 'zip_required', 'boolean', default=True)
    util.create_column(cr, 'res_country', 'state_required', 'boolean', default=False)
    util.new_module(cr, "microsoft_account", deps={"base_setup"})
    util.new_module(cr, "microsoft_calendar", deps={"microsoft_account", "calendar"})

    util.rename_xmlid(cr, *eb('base.module_category_{localization,accounting_localizations}_account_charts'))
    util.remove_record(cr, 'base.module_category_localization')

    util.remove_module(cr, 'hr_expense_check')
