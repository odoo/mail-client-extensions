# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # The name has been reassigned to another lang (ar_AA) with odoo/odoo#28640
    cr.execute(
        "UPDATE res_lang SET name = 'Arabic (Syria) / الْعَرَبيّة' WHERE id = %s", [util.ref(cr, "base.lang_ar_SY")]
    )
