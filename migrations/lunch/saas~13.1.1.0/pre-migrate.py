# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "lunch_supplier", "company_id", "int4")
    cr.execute(
        """
        UPDATE lunch_supplier s
           SET company_id = p.company_id
          FROM res_partner p
         WHERE p.id = s.partner_id
    """
    )

    util.remove_record(cr, "lunch.ir_rule_lunch_product_report_multi_company")

    util.remove_model(cr, "lunch.order.temp")
