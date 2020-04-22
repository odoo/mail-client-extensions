# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "pos_order", "employee_id", "int4")
    util.create_column(cr, "pos_order", "cashier", "varchar")

    cr.execute("""
        UPDATE pos_order po
           SET cashier=e.name
          FROM hr_employee e
         WHERE po.employee_id = e.id"""
    )

    cr.execute("""
        UPDATE pos_order po
           SET cashier=p.name
          FROM res_users u
          JOIN res_partner p ON p.id = u.partner_id
         WHERE cashier IS NULL
           AND po.user_id = u.id"""
    )
