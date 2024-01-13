# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_module(cr, "mrp_subonctracting_landed_costs", "mrp_subcontracting_landed_costs")
    util.rename_module(cr, "website_form_project", "website_project")

    if util.has_enterprise():
        util.rename_module(cr, "account_bacs", "l10n_uk_bacs")
        util.rename_module(cr, "l10n_au_keypay", "l10n_employment_hero")
        util.merge_module(cr, "l10n_be_codabox_bridge", "l10n_be_codabox")
