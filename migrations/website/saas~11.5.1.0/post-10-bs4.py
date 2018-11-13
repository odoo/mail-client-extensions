# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # See https://github.com/odoo/odoo/pull/27981
    cr.execute(
        "UPDATE ir_ui_view SET active=true WHERE id=%s",
        [util.ref(cr, "website.assets_frontend_compatibility_for_12_0")],
    )
