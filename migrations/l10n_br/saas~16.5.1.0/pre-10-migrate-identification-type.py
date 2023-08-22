from odoo.upgrade import util


def migrate(cr, version):
    query = "UPDATE res_partner SET vat = l10n_br_cpf_code WHERE NULLIF(TRIM(vat), '') IS NULL AND l10n_br_cpf_code IS NOT NULL"
    util.explode_execute(cr, query, table="res_partner")
    util.remove_field(cr, "res.partner", "l10n_br_cpf_code", drop_column=False)
