# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE: fields have been copied in point_of_sale@saas~12.5
    util.remove_field(cr, "account.bank.statement.line", "mercury_card_number")
    util.remove_field(cr, "account.bank.statement.line", "mercury_prefixed_card_number")
    util.remove_field(cr, "account.bank.statement.line", "mercury_card_brand")
    util.remove_field(cr, "account.bank.statement.line", "mercury_card_owner_name")
    util.remove_field(cr, "account.bank.statement.line", "mercury_ref_no")
    util.remove_field(cr, "account.bank.statement.line", "mercury_record_no")
    util.remove_field(cr, "account.bank.statement.line", "mercury_invoice_no")

    util.remove_field(cr, "account.journal", "pos_mercury_config_id")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("pos_mercury.res_config_{,settings_}view_form_inherit_pos_mercury"))
    util.rename_xmlid(cr, *eb("pos_mercury.pos_config_view_form_inherit_pos_mercury{_2,}"))

    util.remove_view(cr, "pos_mercury.view_account_journal_pos_user_form")
