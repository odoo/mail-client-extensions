# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Avoid duplicated language name (see odoo/odoo#28640)
    util.force_noupdate(cr, "base.lang_ar_SY", False)
