from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key='account.show_line_subtotals_tax_selection'")
    [show_line] = cr.fetchone() or [None]
    util.create_column(cr, "res_company", "show_line_subtotals_tax_selection", "varchar", default=show_line)
