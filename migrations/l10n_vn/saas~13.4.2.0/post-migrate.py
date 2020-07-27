# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.env(cr).ref("l10n_vn.vn_template").process_coa_translations()
