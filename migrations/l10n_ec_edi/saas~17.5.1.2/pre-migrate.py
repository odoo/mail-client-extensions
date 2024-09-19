from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.company", "l10n_ec_edi_certificate_id", "l10n_ec_edi_certificate_id_old")
    util.create_column(
        cr,
        "res_company",
        "l10n_ec_edi_certificate_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )

    # Create a temporary column to store and retrieve the old certificate ID from the new certificate
    util.create_column(
        cr,
        "certificate_certificate",
        "_upg_old_id",
        "int4",
    )

    cr.execute("""
         WITH old_certificates AS (
            SELECT crt.id AS _upg_old_id,
                   att.id AS att_id,
                   att.name AS name,
                   crt.password AS pkcs12_password,
                   crt.active,
                   crt.company_id
              FROM l10n_ec_edi_certificate AS crt
              JOIN ir_attachment AS att
                ON att.res_id = crt.id
             WHERE att.res_model = 'l10n_ec_edi.certificate'
               AND att.res_field = 'content'
        ), new_certificates AS (
            INSERT INTO certificate_certificate (
                name, pkcs12_password, active, company_id, _upg_old_id
            )
            SELECT name, pkcs12_password, active, company_id, _upg_old_id
              FROM old_certificates
            RETURNING id, _upg_old_id, company_id
        ), update_comp AS (
            UPDATE res_company rc
               SET l10n_ec_edi_certificate_id = nc.id
              FROM new_certificates nc
             WHERE rc.id = nc.company_id
               AND l10n_ec_edi_certificate_id_old = nc._upg_old_id
        )
        UPDATE ir_attachment
           SET res_id = nc.id,
               res_model = 'certificate.certificate',
               res_field = 'content'
          FROM new_certificates nc
         WHERE res_id = nc._upg_old_id
           AND res_model = 'l10n_ec_edi.certificate'
           AND res_field = 'content';
        """)

    util.remove_column(cr, "certificate_certificate", "_upg_old_id")
    util.remove_model(cr, "l10n_ec_edi.certificate")
    util.remove_field(cr, "res.company", "l10n_ec_edi_certificate_id_old")
