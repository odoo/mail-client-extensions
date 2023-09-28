# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "show_update_pricelist", "boolean")
    cr.execute("ALTER TABLE crm_team ALTER COLUMN invoiced_target TYPE float8")

    eb = util.expand_braces
    renames = """
        account_{move_personal_rule,invoice_rule_see_personal}
        account_{move_line_personal_rule,invoice_line_rule_see_personal}
        account_{move,invoice_rule}_see_all
        account_{move_line,invoice_line_rule}_see_all
    """
    for rename in util.splitlines(renames):
        util.rename_xmlid(cr, *eb(f"sale.{rename}"))
