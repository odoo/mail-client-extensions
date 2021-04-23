# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "l10n_nl_kvk", "varchar")
    util.create_column(cr, "res_partner", "l10n_nl_oin", "varchar")
