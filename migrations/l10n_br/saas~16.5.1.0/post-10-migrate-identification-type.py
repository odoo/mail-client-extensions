from odoo.upgrade import util


def migrate(cr, version):
    query = cr.mogrify(
        """
        UPDATE res_partner
           SET l10n_latam_identification_type_id =
             CASE
               WHEN NULLIF(TRIM(l10n_br_cpf_code), '') IS NOT NULL AND l10n_br_cpf_code = vat THEN %s
               ELSE %s
             END
           WHERE country_id = %s and NULLIF(TRIM(vat), '') IS NOT NULL
        """,
        [util.ref(cr, "l10n_br.cpf"), util.ref(cr, "l10n_br.cnpj"), util.ref(cr, "base.br")],
    ).decode()
    util.explode_execute(cr, query, table="res_partner")
    util.remove_column(cr, "res_partner", "l10n_br_cpf_code")
