from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr,
        "res_company",
        "onss_certificate_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )

    cr.execute("""
        WITH old_certificates AS (
            SELECT ia_key.id AS key_id,
                   ia_key.name AS key_name,
                   rc.onss_pem_passphrase AS key_passphrase,
                   ia_crt.id AS crt_id,
                   ia_crt.name AS crt_name,
                   rc.id AS company_id
              FROM ir_attachment ia_key
              JOIN ir_attachment ia_crt
                ON ia_crt.res_id = ia_key.res_id
              JOIN res_company rc
                ON ia_key.res_id = rc.id
             WHERE ia_key.res_model = 'res.company'
               AND ia_key.res_field = 'onss_key'
               AND ia_crt.res_field = 'onss_pem_certificate'
        ), new_keys AS (
            INSERT INTO certificate_key (name, password, company_id, active)
                 SELECT key_name, key_passphrase, company_id, True
                   FROM old_certificates
            RETURNING id, company_id
        ), new_crts AS (
            INSERT INTO certificate_certificate (name, private_key_id, company_id, active)
                 SELECT oc.crt_name, nk.id, oc.company_id, True
                   FROM old_certificates oc
                   JOIN new_keys nk
                     ON oc.company_id = nk.company_id
            RETURNING id, company_id
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
              FROM new_crts nc
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
           SET onss_certificate_id = otnc.res_id
          FROM old_to_new_key otnk
          JOIN old_to_new_crt otnc
            ON otnk.cid = otnc.cid
         WHERE id = otnc.cid;
        """)

    util.remove_field(cr, "res.company", "onss_pem_certificate")
    util.remove_field(cr, "res.company", "onss_key")
    util.remove_field(cr, "res.company", "onss_pem_passphrase")
    util.remove_field(cr, "res.config.settings", "onss_pem_certificate")
    util.remove_field(cr, "res.config.settings", "onss_key")
    util.remove_field(cr, "res.config.settings", "onss_pem_passphrase")
