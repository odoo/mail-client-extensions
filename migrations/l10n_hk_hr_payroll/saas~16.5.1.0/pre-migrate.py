from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_hk_hr_payroll.res_config_settings_view_form_inherit_l10n_hk_hr_payroll")

    util.remove_record(cr, "l10n_hk_hr_payroll.l10n_hk_rule_parameter_internet_1900")
    util.remove_record(cr, "l10n_hk_hr_payroll.l10n_hk_rule_parameter_internet_2019")
    util.remove_record(cr, "l10n_hk_hr_payroll.l10n_hk_rule_parameter_internet")

    cr.execute("DROP VIEW IF EXISTS hr_contract_employee_report")

    cr.execute(
        """
        SELECT parameter_value::numeric
          FROM hr_rule_parameter_value
         WHERE code = 'l10n_hk_wifi_allowance'
           AND date_from < NOW()
         ORDER BY date_from DESC
         LIMIT 1
        """
    )

    internet_allowance = cr.fetchone()[0] if cr.rowcount else 0.0
    cr.execute(
        """
         ALTER TABLE hr_contract
        ALTER COLUMN l10n_hk_internet
                TYPE numeric
               USING CASE WHEN l10n_hk_internet THEN %s ELSE 0.0 END
        """,
        (internet_allowance,),
    )

    util.remove_field(cr, "hr.employee", "l10n_hk_rental_date_start", drop_column=False)
    util.remove_field(cr, "hr.employee", "l10n_hk_rental_amount", drop_column=False)
