def migrate(cr, version):
    cr.execute("DROP TABLE IF EXISTS account_analytic_tag_sale_order_rel")
    cr.execute("DROP TABLE IF EXISTS sale_order_template_tag_rel")
