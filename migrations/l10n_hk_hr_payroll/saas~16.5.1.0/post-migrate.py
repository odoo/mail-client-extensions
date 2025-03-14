from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO l10n_hk_rental (
            create_uid, create_date, write_uid, write_date,
            name, active, employee_id, company_id,
            address,
            state,
            date_start, date_end, amount, nature
        )
        SELECT
               e.create_uid, now() at time zone 'utc', e.write_uid, now() at time zone 'utc',
               e.name, true, e.id, e.company_id,
               CONCAT_WS(', ', e.private_street, e.private_street2, e.private_city, s.name),
               CASE WHEN now() at time zone 'utc' >= e.l10n_hk_rental_date_start THEN 'open' ELSE 'draft' END,
               e.l10n_hk_rental_date_start, NULL, e.l10n_hk_rental_amount, 'flat'
          FROM hr_employee e
     LEFT JOIN res_country_state s ON e.private_state_id = s.id
         WHERE l10n_hk_rental_date_start IS NOT NULL
        """
    )

    util.remove_column(cr, "hr_employee", "l10n_hk_rental_date_start")
    util.remove_column(cr, "hr_employee", "l10n_hk_rental_amount")
