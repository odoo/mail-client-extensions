from odoo.upgrade import util


def migrate(cr, version):
    if util.table_exists(cr, "l10n_co_dian_certificate"):
        _convert_certificates(cr)


def _convert_certificates(cr):
    # Create a temporary column to store and retrieve the old certificate ID from the new certificate
    util.create_column(
        cr,
        "certificate_certificate",
        "_upg_old_id",
        "int4",
        fk_table="l10n_co_dian_certificate",
        on_delete_action="SET NULL",
    )
    util.create_column(
        cr,
        "certificate_key",
        "_upg_old_id",
        "int4",
        fk_table="l10n_co_dian_certificate",
        on_delete_action="SET NULL",
    )

    cr.execute("""
        WITH old_certificates AS (
            SELECT crt.id AS _upg_old_id,
                   crt.company_id AS company_id,
                   att1.name as crt_name,
                   att2.name as key_name
              FROM l10n_co_dian_certificate AS crt
              JOIN ir_attachment AS att1
                ON att1.res_id = crt.id
              JOIN ir_attachment AS att2
                ON att2.res_id = crt.id
             WHERE att1.res_model = 'l10n_co_dian.certificate'
               AND att1.res_field = 'certificate'
               AND att2.res_model = 'l10n_co_dian.certificate'
               AND att2.res_field = 'key'
        ), new_keys AS (
            INSERT INTO certificate_key (
                name, company_id, active, _upg_old_id
            )
                 SELECT key_name, company_id, True, _upg_old_id
                   FROM old_certificates
            RETURNING id, _upg_old_id
        ), new_certificates AS (
            INSERT INTO certificate_certificate (name, company_id, private_key_id, active, _upg_old_id)
                 SELECT oc.crt_name, oc.company_id, nk.id, True, oc._upg_old_id
                   FROM old_certificates oc
                   JOIN new_keys nk
                     ON oc._upg_old_id = nk._upg_old_id
            RETURNING id, _upg_old_id
        ), update_att_key AS (
            UPDATE ir_attachment
               SET res_id = nk.id,
                   res_model = 'certificate.key',
                   res_field = 'content'
              FROM new_keys nk
             WHERE res_id = nk._upg_old_id
               AND res_model = 'l10n_co_dian.certificate'
               AND res_field = 'key'
        )
        UPDATE ir_attachment
           SET res_id = nc.id,
               res_model = 'certificate.certificate',
               res_field = 'content'
          FROM new_keys nc
         WHERE res_id = nc._upg_old_id
           AND res_model = 'l10n_co_dian.certificate'
           AND res_field = 'certificate';
        """)

    util.remove_column(cr, "certificate_key", "_upg_old_id")
    util.remove_column(cr, "certificate_certificate", "_upg_old_id")
    util.remove_model(cr, "l10n_co_dian.certificate")
