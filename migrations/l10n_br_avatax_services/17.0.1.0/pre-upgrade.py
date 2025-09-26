from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "l10n_br_subject_cofins", "varchar", default="T")
    util.create_column(cr, "res_partner", "l10n_br_subject_pis", "varchar", default="T")
    util.create_column(cr, "res_partner", "l10n_br_is_subject_csll", "bool", default=True)
