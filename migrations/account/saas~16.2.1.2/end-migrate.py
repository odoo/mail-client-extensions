# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DELETE FROM ir_config_parameter WHERE key='account.show_line_subtotals_tax_selection'")
