from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr, "res_company", "l10n_ar_afip_ws_key_id", "int4", fk_table="certificate_key", on_delete_action="SET NULL"
    )
    util.create_column(
        cr,
        "res_company",
        "l10n_ar_afip_ws_crt_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )

    cr.execute("""
        WITH old_certificates AS (
            SELECT ia_key.id AS key_id,
                   ia_key.name AS key_name,
                   ia_crt.id AS crt_id,
                   ia_crt.name AS crt_name,
                   ia_key.res_id AS company_id
              FROM ir_attachment ia_key
              JOIN ir_attachment ia_crt
                ON ia_crt.res_id = ia_key.res_id
             WHERE ia_key.res_model = 'res.company'
               AND ia_key.res_field = 'l10n_ar_afip_ws_key'
               AND ia_crt.res_field = 'l10n_ar_afip_ws_crt'
        ), new_keys AS (
            INSERT INTO certificate_key (name, company_id, active)
                 SELECT key_name, company_id, True
                   FROM old_certificates
            RETURNING company_id, id
        ), new_certificates AS (
            INSERT INTO certificate_certificate (name, company_id, private_key_id, active)
                 SELECT oc.crt_name, oc.company_id, nk.id, True
                   FROM old_certificates oc
                   JOIN new_keys nk
                     ON oc.company_id = nk.company_id
            RETURNING company_id, id
        ), old_to_new_key AS (
            SELECT nk.company_id AS cid,
                   nk.id AS res_id,
                   'certificate.key' AS res_model,
                   oc.key_id AS att_id
              FROM new_keys nk
              JOIN old_certificates oc
                ON nk.company_id = oc.company_id
        ), old_to_new_crt AS (
            SELECT nc.company_id AS cid,
                   nc.id AS res_id,
                   'certificate.certificate' AS res_model,
                   oc.crt_id AS att_id
              FROM new_certificates nc
              JOIN old_certificates oc
                ON nc.company_id = oc.company_id
        ), updated_att AS (
            UPDATE ir_attachment
               SET res_id = otn.res_id,
                   res_model = otn.res_model,
                   res_field = 'content'
              FROM (
                           SELECT * FROM old_to_new_key
                     UNION SELECT * FROM old_to_new_crt
                   ) AS otn
             WHERE id = otn.att_id
        )
        UPDATE res_company
           SET l10n_ar_afip_ws_key_id = otnk.res_id,
               l10n_ar_afip_ws_crt_id = otnc.res_id
          FROM old_to_new_key otnk
          JOIN old_to_new_crt otnc
            ON otnk.cid = otnc.cid
         WHERE id = otnk.cid;
        """)

    util.remove_field(cr, "res.company", "l10n_ar_afip_ws_crt")
    util.remove_field(cr, "res.company", "l10n_ar_afip_ws_key")
    util.remove_field(cr, "res.company", "l10n_ar_afip_ws_crt_fname")
    util.remove_field(cr, "res.config.settings", "l10n_ar_afip_ws_crt")
    util.remove_field(cr, "res.config.settings", "l10n_ar_afip_ws_key")
    util.remove_field(cr, "res.config.settings", "l10n_ar_afip_ws_key_fname")
    util.remove_field(cr, "res.config.settings", "l10n_ar_afip_ws_crt_fname")
