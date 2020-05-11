# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "is_tax_closing", "boolean")
    util.create_column(cr, "res_company", "account_tax_periodicity", "varchar")
    util.create_column(cr, "res_company", "account_tax_periodicity_reminder_day", "int4")
    util.create_column(cr, "res_company", "account_tax_original_periodicity_reminder_day", "int4")
    util.create_column(cr, "res_company", "account_tax_periodicity_journal_id", "int4")
    util.create_column(cr, "res_company", "account_tax_next_activity_type", "int4")

    cr.execute("""
        UPDATE res_company
           SET account_tax_periodicity='monthly',
               account_tax_periodicity_reminder_day=7
    """)

    cr.execute(
        """
        WITH min_journal_ids AS (
            SELECT company_id, 
                   min (CASE WHEN show_on_dashboard THEN id ELSE NULL END) AS dashboard_min_id,
                   min (id) AS min_id
              FROM account_journal
             WHERE type='general'
            GROUP BY company_id
        )
        UPDATE res_company c
           SET account_tax_periodicity_journal_id = COALESCE(mid.dashboard_min_id, mid.min_id)
          FROM min_journal_ids mid
         WHERE mid.company_id = c.id
           AND account_tax_periodicity_journal_id IS NULL
        """
    )
