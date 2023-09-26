from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_au_keypay.keypay_sync_cron", "l10n_employment_hero.employment_hero_sync_cron")
    util.rename_xmlid(
        cr, "l10n_au_keypay.action_kp_payroll_fetch_payrun", "l10n_employment_hero.action_eh_payroll_fetch_payrun"
    )

    fields_to_rename = [
        ("account.move", "l10n_au_kp_payrun_identifier", "employment_hero_payrun_identifier"),
        ("account.account", "l10n_au_kp_account_identifier", "employment_hero_account_identifier"),
        ("account.account", "l10n_au_kp_enable", "employment_hero_enable"),
        ("account.tax", "l10n_au_kp_tax_identifier", "employment_hero_tax_identifier"),
        ("account.tax", "l10n_au_kp_enable", "employment_hero_enable"),
        ("res.company", "l10n_au_kp_enable", "employment_hero_enable"),
        ("res.company", "l10n_au_kp_identifier", "employment_hero_identifier"),
        ("res.company", "l10n_au_kp_lock_date", "employment_hero_lock_date"),
        ("res.company", "l10n_au_kp_journal_id", "employment_hero_journal_id"),
        ("res.config.settings", "l10n_au_kp_enable", "employment_hero_enable"),
        ("res.config.settings", "l10n_au_kp_identifier", "employment_hero_identifier"),
        ("res.config.settings", "l10n_au_kp_lock_date", "employment_hero_lock_date"),
        ("res.config.settings", "l10n_au_kp_journal_id", "employment_hero_journal_id"),
    ]

    for model, old_field_name, new_field_name in fields_to_rename:
        util.rename_field(cr, model, old_field_name, new_field_name)

    # These two fields were on the res.config.settings as a config_parameter fields => we remove them, and add them back on the company
    util.remove_field(cr, "res.config.settings", "l10n_au_kp_api_key")
    util.remove_field(cr, "res.config.settings", "l10n_au_kp_base_url")
    util.create_column(cr, "res_company", "employment_hero_api_key", "varchar")
    util.create_column(cr, "res_company", "employment_hero_base_url", "varchar")
    # Then we migrate the value from the config parameter to the new fields, and finally we remove these.
    cr.execute(
        """
        UPDATE res_company
           SET employment_hero_api_key = (SELECT value
                                          FROM ir_config_parameter
                                          WHERE key='l10n_au_keypay.l10n_au_kp_api_key'
                                          ),
               employment_hero_base_url = (SELECT value
                                           FROM ir_config_parameter
                                           WHERE key='l10n_au_keypay.l10n_au_kp_base_url'
                                          )
        WHERE employment_hero_enable IS TRUE
    """
    )
    cr.execute(
        "DELETE FROM ir_config_parameter WHERE key in ('l10n_au_keypay.l10n_au_kp_api_key', 'l10n_au_keypay.l10n_au_kp_base_url')"
    )
