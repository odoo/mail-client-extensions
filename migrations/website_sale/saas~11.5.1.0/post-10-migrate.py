# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.ENVIRON.get("S115_default_cart_recovery_template"):
        cr.execute(
            "UPDATE website SET cart_recovery_mail_template_id=%s",
            [util.ref(cr, "website_sale.mail_template_sale_cart_recovery")],
        )
