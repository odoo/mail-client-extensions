from dateutil.relativedelta import relativedelta

from odoo import Command
from odoo.tools.misc import format_date

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute(
        """
        WITH closing_moves AS (
            SELECT move.id AS move_id,
                   move.date,
                   company.id AS company_id,
                   rtrn_type.id AS return_type_id,
                   rtrn_type.name AS return_name,
                   COALESCE(rtrn_type.deadline_periodicity, company.account_return_periodicity) AS periodicity,
                   LAG(move.date) OVER (
                       PARTITION BY move.company_id
                       ORDER BY move.date
                   ) AS prev_move_date,
                   COALESCE(report.country_id, company.account_fiscal_country_id) AS tax_country_id,
                   EXISTS (
                       SELECT 1
                         FROM mail_activity activity
                        WHERE activity.res_id = move.id
                          AND activity.res_model = 'account.move'
                          AND activity.activity_type_id = %s
                   ) AS has_to_pay_activity
              FROM account_move move
              JOIN account_return_type rtrn_type
                ON move.tax_closing_report_id = rtrn_type.report_id
              JOIN res_company company
                ON move.company_id = company.id
              JOIN account_report report
                ON report.id = move.tax_closing_report_id
             WHERE move.tax_closing_report_id IS NOT NULL
               AND move.state = 'posted'
        ),
        tax_accounts AS (
            SELECT tax.company_id,
                   tax.country_id,
                   ARRAY_AGG(DISTINCT tax_group.tax_payable_account_id) AS payable_accounts,
                   ARRAY_AGG(DISTINCT tax_group.tax_receivable_account_id) AS receivable_accounts
              FROM account_tax tax
              JOIN account_tax_group tax_group
                ON tax.tax_group_id = tax_group.id
             GROUP BY tax.company_id, tax.country_id
        ),
        amounts_by_move AS (
            SELECT move.move_id,
                   COALESCE(
                       -SUM(
                           CASE
                               WHEN (
                                   (aml.account_id = ANY(account.payable_accounts) AND aml.credit > 0) OR
                                   (aml.account_id = ANY(account.receivable_accounts) AND aml.debit > 0)
                               ) THEN aml.balance
                               ELSE 0
                           END
                       ), 0
                   ) AS amount
              FROM closing_moves move
              JOIN account_move_line aml
                ON aml.move_id = move.move_id
              JOIN tax_accounts account
                ON account.company_id = move.company_id
               AND account.country_id = move.tax_country_id
             GROUP BY move.move_id
        )
        SELECT move.move_id,
               CASE
                   WHEN move.prev_move_date IS NULL THEN
                       CASE
                           WHEN periodicity = 'yearly'     THEN move.date - INTERVAL '1 year'
                           WHEN periodicity = 'semester'   THEN move.date - INTERVAL '6 months'
                           WHEN periodicity = '4_months'   THEN move.date - INTERVAL '4 months'
                           WHEN periodicity = 'trimester'  THEN move.date - INTERVAL '3 months'
                           WHEN periodicity = '2_months'   THEN move.date - INTERVAL '2 months'
                           ELSE move.date - INTERVAL '1 month'
                       END
                   ELSE move.prev_move_date + INTERVAL '1 day'
               END AS date_from,
               move.date AS date_to,
               move.company_id,
               move.return_type_id,
               COALESCE(move.return_name ->> %s, move.return_name ->> 'en_US') AS return_name,
               CASE
                   WHEN move.has_to_pay_activity THEN 'submitted'
                   ELSE 'paid'
               END AS state,
               amounts_by_move.amount
          FROM closing_moves move
          JOIN amounts_by_move
            ON move.move_id = amounts_by_move.move_id
         ORDER BY move.company_id, move.date
        """,
        [util.ref(cr, "account_reports.mail_activity_type_tax_report_to_pay"), env.user.lang],
    )

    query_res = cr.fetchall()
    return_create_vals = []
    for res in query_res:
        move_id, date_from, date_to, company_id, return_type_id, return_type_name, state, amount = res
        periodicities_mapping = {
            12: "year",
            6: "semester",
            4: "4_months",
            3: "trimester",
            2: "2_months",
            1: "monthly",
        }
        delta = relativedelta(date_to, date_from + relativedelta(days=-1))
        months_periodicity = delta.years * 12 + delta.months
        periodicity = periodicities_mapping.get(months_periodicity, "other")
        if periodicity == "year":
            period_suffix = f"{date_from.year}"
        elif periodicity == "trimester":
            period_suffix = f"{format_date(env, date_from, date_format='qqq yyyy')}"
        elif periodicity == "monthly":
            period_suffix = f"{format_date(env, date_from, date_format='LLLL yyyy')}"
        else:
            period_suffix = f"{format_date(env, date_from)} - {format_date(env, date_to)}"
        name = f"{return_type_name} {period_suffix}"
        return_create_vals.append(
            {
                "name": name,
                "type_id": return_type_id,
                "company_id": company_id,
                "date_from": date_from,
                "date_to": date_to,
                "date_submission": date_to,
                "is_completed": state == "paid",
                "state": state,
                "closing_move_ids": [Command.link(move_id)],
                "amount_to_pay": amount,
            }
        )

    env["account.return"].create(return_create_vals)
    cr.commit()

    # Move attachments from moves to returns
    util.explode_execute(
        cr,
        """
        UPDATE ir_attachment att
           SET res_model='account.return',
               res_id=move.closing_return_id
          FROM account_move move
         WHERE att.res_model='account.move'
           AND att.res_id = move.id
           AND move.closing_return_id IS NOT NULL
        """,
        table="ir_attachment",
        alias="att",
    )
    cr.execute(
        """
        INSERT INTO account_return_ir_attachment_rel(
                        account_return_id, ir_attachment_id
                    )
             SELECT res_id, id
               FROM ir_attachment
              WHERE res_model='account.return'
        """
    )

    activity_type_xmlids = [
        "account_reports.mail_activity_type_tax_report_to_pay",
        "account_reports.mail_activity_type_tax_report_to_be_sent",
        "account_reports.mail_activity_type_tax_report_error",
        "account_reports.tax_closing_activity_type",
    ]
    activity_type_ids = list(filter(None, (util.ref(cr, xmlid) for xmlid in activity_type_xmlids)))
    cr.execute(
        """
        UPDATE mail_activity
           SET activity_type_id = NULL
         WHERE activity_type_id = ANY(%s)
        """,
        [activity_type_ids],
    )
    util.delete_unused(cr, "mail.activity.type", *activity_type_xmlids)
    util.change_field_selection_values(cr, "mail.activity.type", "category", {"tax_report": None})

    """
    Previously, tax closing moves were generated in draft mode,
    requiring the user to manually review and post them.
    Now, the process has changed: closing moves are generated directly
    from account.return objects and are created in a posted state,
    since the returns themselves are now prepared in advance.
    Therefore, we no longer need those draft closing moves and removing them
    to prevent any confusion or accidental manual posting by users later on.
    """
    cr.execute(
        """
        SELECT id
          FROM account_move
         WHERE state = 'draft'
           AND tax_closing_report_id IS NOT NULL
        """
    )
    move_ids = [mid for (mid,) in cr.fetchall()]
    util.remove_records(cr, "account.move", move_ids)
    util.remove_field(cr, "account.move", "tax_closing_report_id")
