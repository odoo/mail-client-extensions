from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("TRUNCATE TABLE l10n_co_dian_operation_mode")
    if util.column_exists(cr, "res_partner", "l10n_co_dian_software_id"):
        cr.execute(
            """
                INSERT INTO l10n_co_dian_operation_mode (
                    dian_software_id,
                    dian_software_security_code,
                    dian_software_operation_mode,
                    dian_testing_id,
                    company_id
                )
                SELECT l10n_co_dian_software_id,
                       l10n_co_dian_software_security_code,
                       'invoice',
                       l10n_co_dian_testing_id,
                       id
                  FROM res_company
                 WHERE l10n_co_dian_software_id IS NOT NULL
                   AND l10n_co_dian_software_security_code IS NOT NULL;
            """
        )

    util.remove_field(cr, "res.config.settings", "l10n_co_dian_software_id")
    util.remove_field(cr, "res.config.settings", "l10n_co_dian_software_security_code")
    util.remove_field(cr, "res.config.settings", "l10n_co_dian_testing_id")
    util.remove_column(cr, "res_company", "l10n_co_dian_software_id")
    util.remove_column(cr, "res_company", "l10n_co_dian_software_security_code")
    util.remove_column(cr, "res_company", "l10n_co_dian_testing_id")
