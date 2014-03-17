# -*- coding: utf-8 -*-
def migrate(cr, version):
    # if present, these views forbid the size change of the column "name" of product_template
    cr.execute("DROP VIEW IF EXISTS report_sales_by_margin_pos")
    cr.execute("DROP VIEW IF EXISTS report_sales_by_margin_pos_month")
