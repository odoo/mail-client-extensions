# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        "UPDATE res_company SET stock_mail_confirmation_template_id=%s",
        [util.ref(cr, "stock.mail_template_data_delivery_confirmation")],
    )

    util.env(cr)["res.company"].create_missing_scrap_sequence()
