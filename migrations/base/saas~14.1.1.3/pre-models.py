# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "mobile", "varchar")
    cr.execute(
        """
            UPDATE res_company c
               SET mobile = p.mobile
              FROM res_partner p
             WHERE p.id = c.partner_id
        """
    )
