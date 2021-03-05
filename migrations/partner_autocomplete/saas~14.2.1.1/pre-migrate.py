# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # at migration, consider all companies are already enriched (avoid unnecessary calls to IAP)
    # but still keep as default=False in database (aka, do not use default=True)
    util.create_column(cr, "res_company", "iap_enrich_auto_done", "boolean")
    cr.execute("UPDATE res_company SET iap_enrich_auto_done = true")
