from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "ir.actions.server ", "ai_prompt")
