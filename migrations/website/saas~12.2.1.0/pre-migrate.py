# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.partner", "is_published", "website_partner", "website")
    util.create_column(cr, "res_partner", "is_published", "boolean")

    cr.execute(
        "UPDATE ir_ui_view SET customize_show = FALSE WHERE id = %s", [util.ref(cr, "portal.portal_show_sign_in")]
    )

    util.convert_binary_field_to_attachment(cr, "website", "favicon")
