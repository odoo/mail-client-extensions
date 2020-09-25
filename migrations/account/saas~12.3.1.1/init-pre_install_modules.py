#!/usr/bin/python


def prepare_migration(cr):
    # This is normally handled in an upgrade script
    # upgrade/migrations/account/0.0.0/pre-l10n-xmlids-from-templates.py
    # But here, as we are installing modules before upgrade, the script has not the chance to be executed
    # and records not correctly marked as noupdate might be deleted, preventing the upgrade
    # e.g. Deleting 887@account.account (l10n_lu.1_lu_2020_account_703001)
    cr.execute(
        """
        UPDATE ir_model_data
           SET noupdate = True
         WHERE module like 'l10n_%'
           AND noupdate = False
           AND model in (
               'account.account',
               'account.tax',
               'account.fiscal.position',
               'account.fiscal.position.account',
               'account.fiscal.position.tax'
        )
    """
    )

    # `account_reports` is required for the upgrade from 12.0 to saas-12.3/13.0 when account is installed.
    # To correctly migrate taxes, 'l10n_x_reports' needs also to be installed when 'l10n_x' is installed
    # for some country codes x.
    # note: more info about EXCLUDED here https://www.postgresql.org/docs/9.5/sql-insert.html#AEN85938
    cr.execute(
        """
             INSERT INTO ir_config_parameter AS icp (key, value)
             SELECT 'upgrade.pre_install_modules', string_agg(name, ',') as names
                    FROM (
                        SELECT name FROM ir_module_module WHERE name = 'account_reports' AND state = 'uninstalled'
                         UNION
                        SELECT r.name
                          FROM ir_module_module m
                          JOIN ir_module_module r ON r.name = m.name || '_reports'
                         WHERE m.name ~ 'l10n_.+' and m.state = 'installed' and r.state = 'uninstalled'
                    ) x
             HAVING COUNT(*) > 0
        ON CONFLICT (key) DO UPDATE SET value = COALESCE(ltrim(icp.value || ',' || EXCLUDED.value, ','), '')
    """
    )

    # The l10n_x module needs to be updated too since modifications to it may have broken references to its data
    cr.execute(
        """
             INSERT INTO ir_config_parameter AS icp (key, value)
             SELECT 'upgrade.pre_update_modules', string_agg(name, ',') as names
               FROM ir_module_module
              WHERE name ~ 'l10n_.+' AND state = 'installed' HAVING count(*) > 0
        ON CONFLICT (key) DO UPDATE SET value = COALESCE(ltrim(icp.value || ',' || EXCLUDED.value, ','), '')
    """
    )
