# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_module(cr, "l10n_de_purchase", "l10n_din5008_purchase")
    util.rename_module(cr, "l10n_de_repair", "l10n_din5008_repair")
    util.rename_module(cr, "l10n_de_sale", "l10n_din5008_sale")
    util.rename_module(cr, "l10n_de_stock", "l10n_din5008_stock")

    util.modules_auto_discovery(cr)

    util.remove_module(cr, "note_pad")
    util.remove_module(cr, "pad_project")
    util.remove_module(cr, "pad")
    util.remove_module(cr, "project_account")

    util.force_upgrade_of_fresh_module(cr, "l10n_din5008")
