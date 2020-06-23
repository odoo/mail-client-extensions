# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT demo FROM ir_module_module WHERE name='base'")
    demo = cr.fetchone()[0]
    if not demo:
        util.delete_unused(
            cr,
            "utm.utm_campaign_fall_drive",
            "utm.utm_campaign_christmas_special",
            "utm.utm_campaign_email_campaign_services",
            "utm.utm_campaign_email_campaign_products",
        )
