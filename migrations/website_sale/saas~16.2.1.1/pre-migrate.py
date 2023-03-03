from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key='account.show_line_subtotals_tax_selection'")
    [show_line] = cr.fetchone() or [None]
    util.create_column(cr, "res_company", "show_line_subtotals_tax_selection", "varchar", default=show_line)
    util.rename_xmlid(cr, "website_sale.menu_ecommerce_payment_icons", "website_sale.menu_ecommerce_payment_methods")
    util.remove_view(cr, "website_sale.view_quotation_tree")
    util.rename_xmlid(cr, "website_sale.view_order_tree", "website_sale.sale_order_tree")
