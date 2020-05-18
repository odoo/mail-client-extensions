# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        "UPDATE ir_ui_view SET active=true WHERE id=%s",
        [util.ref(cr, "web_editor._assets_13_0_color_system_support_primary_variables")],
    )
