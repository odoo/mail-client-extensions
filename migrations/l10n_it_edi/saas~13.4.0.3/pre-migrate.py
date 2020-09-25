# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "account_move", "l10n_it_einvoice_name")
    util.remove_column(cr, "account_move", "l10n_it_einvoice_id")
