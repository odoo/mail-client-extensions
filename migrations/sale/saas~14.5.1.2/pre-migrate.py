# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "template_id", "invoice_mail_template_id")
    util.rename_field(cr, "res.config.settings", "confirmation_template_id", "confirmation_mail_template_id")

    cr.execute(
        """
        UPDATE ir_config_parameter
           SET key = 'sale.default_invoice_email_template'
         WHERE key = 'sale.default_email_template';
        """
    )

    # ===============================================================
    # Withholding taxes (Task 2457374 - PR 74138)
    # ===============================================================
    util.remove_field(cr, "sale.order", "amount_by_group")
