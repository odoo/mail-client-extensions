from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr,
        "res_company",
        "l10n_nl_reports_sbr_cert_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )
    util.create_column(
        cr,
        "res_company",
        "l10n_nl_reports_sbr_server_root_cert_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )

    # Create a temporary column to store and retrieve the att ID from the new key/certificate
    util.create_column(cr, "certificate_key", "_upg_att_id", "int4")
    util.create_column(cr, "certificate_certificate", "_upg_att_id", "int4")

    cr.execute("""
        WITH old_certificates AS (
            SELECT rc.id AS company_id,
                   ia.id AS _upg_att_id,
                   ia.res_field AS field,
                   rc.l10n_nl_reports_sbr_key_filename AS key_name,
                   rc.l10n_nl_reports_sbr_cert_filename AS crt_name,
                   rcs.l10n_nl_reports_sbr_password AS password
              FROM res_company AS rc
              JOIN ir_attachment AS ia
                ON ia.res_id = rc.id
              LEFT
              JOIN res_config_settings AS rcs
                ON rcs.company_id = rc.id
             WHERE ia.res_model = 'res.company'
               AND ia.res_field IN ('l10n_nl_reports_sbr_cert', 'l10n_nl_reports_sbr_key', 'l10n_nl_reports_sbr_server_root_cert')
        ), new_keys AS (
            INSERT INTO certificate_key (
                company_id, name, password, active, _upg_att_id
            )
            SELECT company_id, key_name, password, True, _upg_att_id
              FROM old_certificates
             WHERE field = 'l10n_nl_reports_sbr_key'
            RETURNING company_id, id, _upg_att_id, 'certificate.key' AS model
        ), new_certificates AS (
            INSERT INTO certificate_certificate (
                company_id, name, private_key_id, active, _upg_att_id
            )
            SELECT oc.company_id, crt_name, nk.id, True, oc._upg_att_id
              FROM old_certificates oc
              JOIN new_keys nk
                ON nk.company_id = oc.company_id
             WHERE oc.field = 'l10n_nl_reports_sbr_cert'
            RETURNING company_id, id, _upg_att_id, 'certificate.certificate' AS model
        ), new_root_certificates AS (
            INSERT INTO certificate_certificate (
                company_id, name, active, _upg_att_id
            )
            SELECT oc.company_id, oc.crt_name, True, _upg_att_id
              FROM old_certificates oc
             WHERE oc.field = 'l10n_nl_reports_sbr_server_root_cert'
            RETURNING company_id, id, _upg_att_id, 'certificate.certificate' AS model
        ), updated_comp AS (
            UPDATE res_company rc
               SET l10n_nl_reports_sbr_cert_id = nc.id,
                   l10n_nl_reports_sbr_server_root_cert_id = nrc.id
              FROM new_certificates nc
              JOIN new_root_certificates nrc
                ON nrc.company_id = nc.company_id
             WHERE rc.id = nc.company_id
        )
        UPDATE ir_attachment ia
           SET res_id = t.new_id,
               res_model = t.model,
               res_field = 'content'
          FROM (
               SELECT * FROM new_keys
                UNION
               SELECT * FROM new_certificates
                UNION
               SELECT * FROM new_root_certificates
          ) AS t(company_id, new_id, _upg_att_id, model)
         WHERE ia.id = t._upg_att_id;
        """)

    util.remove_column(cr, "certificate_key", "_upg_att_id")
    util.remove_column(cr, "certificate_certificate", "_upg_att_id")
    util.remove_field(cr, "res.config.settings", "l10n_nl_reports_sbr_key")
    util.remove_field(cr, "res.config.settings", "l10n_nl_reports_sbr_cert")
    util.remove_field(cr, "res.config.settings", "l10n_nl_reports_sbr_cert_filename")
    util.remove_field(cr, "res.config.settings", "l10n_nl_reports_sbr_key_filename")
    util.remove_field(cr, "res.config.settings", "l10n_nl_reports_sbr_password")
    util.remove_field(cr, "res.company", "l10n_nl_reports_sbr_key")
    util.remove_field(cr, "res.company", "l10n_nl_reports_sbr_cert")
    util.remove_field(cr, "res.company", "l10n_nl_reports_sbr_server_root_cert")
    util.remove_field(cr, "res.company", "l10n_nl_reports_sbr_cert_filename")
    util.remove_field(cr, "res.company", "l10n_nl_reports_sbr_key_filename")
