# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, "product_template", "hr_expense_ok", "boolean")
    cr.execute("UPDATE product_template SET hr_expense_ok = 'f'")
    cr.execute("""UPDATE product_template t
                     SET hr_expense_ok = 't'
                    FROM product_product p
                   WHERE t.id = p.product_tmpl_id
                     AND p.hr_expense_ok
               """)
    util.remove_field(cr, "product.product", "hr_expense_ok")
