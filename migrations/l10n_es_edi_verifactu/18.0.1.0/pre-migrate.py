from odoo.upgrade import util


def migrate(cr, version):
    # Move data from model `l10n_es_edi_verifactu.certificate` into "standard" model `certificate.certificate`

    # Create a temporary column to store and retrieve the old certificate ID from the new certificate
    util.create_column(
        cr,
        "certificate_certificate",
        "_upg_old_id",
        "int4",
    )

    cr.execute("""
        WITH old_certificates AS (
            SELECT cert.id, att.name, cert.password, cert.company_id
              FROM l10n_es_edi_verifactu_certificate AS cert
              JOIN ir_attachment att
                ON att.res_id = cert.id
             WHERE att.res_model = 'l10n_es_edi_verifactu.certificate'
               AND att.res_field = 'content'
        ), new_certificates AS (
            INSERT INTO certificate_certificate (name, pkcs12_password, company_id, scope, active, _upg_old_id)
                 SELECT name, password, company_id, 'verifactu', True, id
                   FROM old_certificates
            RETURNING id, _upg_old_id, company_id
        )
        UPDATE ir_attachment att
           SET res_id = new_cert.id,
               res_model = 'certificate.certificate'
          FROM new_certificates new_cert
         WHERE res_id = new_cert._upg_old_id
           AND res_model = 'l10n_es_edi_verifactu.certificate'
           AND res_field = 'content';
        """)

    util.remove_column(cr, "certificate_certificate", "_upg_old_id")
    util.remove_model(cr, "l10n_es_edi_verifactu.certificate")
