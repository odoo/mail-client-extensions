# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.str2bool(os.getenv("UPG_NO_REINDEX_IMD", "0")):
        return False
    cr.execute("REINDEX TABLE ir_model_data")
