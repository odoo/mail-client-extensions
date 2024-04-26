from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "res_company", "sepa_pain_version")
