# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "adyen.account")
    util.remove_model(cr, "adyen.store")
    util.remove_model(cr, "adyen.terminal")

    util.remove_field(cr, "res.config.settings", "adyen_account_id")
    util.remove_field(cr, "pos.payment.method", "adyen_account_id")
    util.remove_field(cr, "pos.payment.method", "adyen_terminal_id")

    util.remove_record(cr, "pos_adyen.action_pos_adyen_account")
    util.remove_record(cr, "pos_adyen.menu_pos_adyen_account")

    util.remove_view(cr, "pos_adyen.res_config_settings_view_form")
