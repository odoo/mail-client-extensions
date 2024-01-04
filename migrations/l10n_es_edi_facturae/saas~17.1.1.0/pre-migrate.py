from odoo.upgrade import util


def migrate(cr, version):
    if util.table_exists(cr, "l10n_es_edi_facturae_adm_centers_ac_role_type_res_partner_rel"):
        cr.execute(
            """
            ALTER TABLE l10n_es_edi_facturae_adm_centers_ac_role_type_res_partner_rel
              RENAME TO l10n_es_edi_facturae_ac_role_type_res_partner_rel
            """
        )
        cr.execute(
            """
              ALTER TABLE l10n_es_edi_facturae_ac_role_type_res_partner_rel
            RENAME COLUMN l10n_es_edi_facturae_adm_centers_ac_role_type_id
                       TO l10n_es_edi_facturae_ac_role_type_id
            """
        )
    util.rename_model(cr, "l10n_es_edi_facturae_adm_centers.ac_role_type", "l10n_es_edi_facturae.ac_role_type")
