# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # res.city has been moved to l10n_mx_edi_extended in v15 https://github.com/odoo/upgrade/pull/3193
    cr.execute("SELECT 1 FROM ir_model_fields WHERE model='res.partner' AND name='city_id'")
    if not cr.rowcount:
        return
    util.force_install_module(cr, "l10n_mx_edi_extended")
    util.force_upgrade_of_fresh_module(cr, "l10n_mx_edi_extended")
