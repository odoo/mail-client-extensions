from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "quality_point", "worksheet_model_name")
