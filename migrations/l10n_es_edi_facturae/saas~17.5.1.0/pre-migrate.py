from odoo.upgrade import util


def migrate(cr, version):
    # Create a temporary column to store and retrieve the attachment ID from the new certificate
    util.create_column(
        cr,
        "certificate_certificate",
        "_upg_att_id",
        "int4",
    )

    cr.execute("""
        WITH old_certificates AS (
            SELECT ia.name, ia.id AS _upg_att_id, cert.password, cert.company_id
              FROM l10n_es_edi_facturae_certificate AS cert
              JOIN ir_attachment ia
                ON ia.res_id = cert.id
             WHERE ia.res_model = 'l10n_es_edi_facturae.certificate'
               AND ia.res_field = 'content'
        ), new_certificates AS (
            INSERT INTO certificate_certificate (name, pkcs12_password, company_id, scope, active, _upg_att_id)
                 SELECT name, password, company_id, 'facturae', True, _upg_att_id
                   FROM old_certificates
            RETURNING id, _upg_att_id
        )
        UPDATE ir_attachment ia
           SET res_id = nc.id,
               res_model = 'certificate.certificate',
               res_field = 'content'
          FROM new_certificates nc
         WHERE ia.id = nc._upg_att_id;
        """)

    util.remove_column(cr, "certificate_certificate", "_upg_att_id")
    util.remove_field(cr, "res.company", "l10n_es_edi_facturae_certificate_id")
    util.remove_model(cr, "l10n_es_edi_facturae.certificate")
    util.remove_view(cr, "l10n_es_edi_facturae.view_company_form_inherit_l10n_es_edi_facturae")
