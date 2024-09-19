from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr,
        "certificate_certificate",
        "user_id",
        "int4",
        fk_table="res_users",
        on_delete_action="SET NULL",
    )
    util.create_column(cr, "certificate_certificate", "last_token", "varchar")
    util.create_column(cr, "certificate_certificate", "token_time", "date")
    util.create_column(cr, "certificate_certificate", "last_rest_token", "varchar")
    util.create_column(cr, "certificate_certificate", "subject_serial_number", "varchar")

    # Create a temporary column to store and retrieve the attachment ID from the new certificate
    util.create_column(
        cr,
        "certificate_certificate",
        "_upg_att_id",
        "int4",
    )

    cr.execute("""
        WITH old_certificates AS (
            SELECT att.id AS _upg_att_id,
                   crt.signature_filename AS name,
                   crt.signature_pass_phrase AS pkcs12_password,
                   crt.user_id,
                   crt.last_token,
                   crt.token_time,
                   crt.last_rest_token,
                   crt.company_id,
                   crt.subject_serial_number
              FROM l10n_cl_certificate AS crt
              JOIN ir_attachment AS att
                ON res_id = crt.id
             WHERE res_model = 'l10n_cl.certificate'
               AND res_field = 'signature_key_file'
        ), new_crts AS (
            INSERT INTO certificate_certificate (
                name, pkcs12_password, company_id, active, _upg_att_id, subject_serial_number
            )
            SELECT name, pkcs12_password, company_id, True, _upg_att_id, subject_serial_number
              FROM old_certificates oc
            RETURNING _upg_att_id, id
        )
        UPDATE ir_attachment ia
           SET res_id = nc.id,
               res_model = 'certificate.certificate',
               res_field = 'content'
          FROM new_crts nc
         WHERE ia.id = nc._upg_att_id;
        """)

    util.remove_column(cr, "certificate_certificate", "_upg_att_id")

    util.remove_model(cr, "l10n_cl.certificate")
    util.remove_record(cr, "l10n_cl_edi.l10n_cl_certificate_comp_rule")
