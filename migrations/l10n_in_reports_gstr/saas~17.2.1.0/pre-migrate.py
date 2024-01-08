# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_company
           SET l10n_in_edi_production_env = TRUE
         WHERE l10n_in_gstr_gst_production_env IS TRUE;
    """
    )

    util.remove_field(cr, "res.company", "l10n_in_gstr_gst_production_env")
    util.remove_field(cr, "res.config.settings", "l10n_in_gstr_gst_production_env")
