from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "website", "show_line_subtotals_tax_selection", "varchar")

    cr.execute(
        """
        UPDATE website w
           SET show_line_subtotals_tax_selection = c.show_line_subtotals_tax_selection
          FROM res_company c
         WHERE c.id = w.company_id
    """
    )
    util.remove_field(cr, "res.company", "show_line_subtotals_tax_selection")
    util.remove_column(cr, "sale_order", "amount_delivery")
    util.move_field_to_module(cr, "sale.report", "is_abandoned_cart", "website_sale_dashboard", "website_sale")
