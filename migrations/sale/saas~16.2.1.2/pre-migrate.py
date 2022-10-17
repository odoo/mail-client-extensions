# -*- coding: utf-8 -*-

from odoo.tools.misc import str2bool

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order.cancel", "email_from")
    util.remove_field(cr, "res.config.settings", "use_quotation_validity_days")
    util.remove_column(cr, "res_config_settings", "deposit_default_product_id")

    env = util.env(cr)
    ICP = env["ir.config_parameter"]
    util.remove_constraint(cr, "res_company", "res_company_check_quotation_validity_days")
    use_quotation_validity_days = str2bool(ICP.get_param("sale.use_quotation_validity_days"))
    if not use_quotation_validity_days:
        cr.execute("""UPDATE res_company SET quotation_validity_days = 0""")

    default_deposit_product_id = ICP.get_param("sale.default_deposit_product_id", False)
    util.create_column(
        cr, "res_company", "sale_down_payment_product_id", "int4", default=default_deposit_product_id or None
    )
    cr.execute(
        """
        DELETE FROM ir_config_parameter
        WHERE key in ('sale.use_quotation_validity_days', 'sale.default_deposit_product_id')
        """
    )
