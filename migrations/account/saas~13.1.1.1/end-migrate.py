# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO account_tax_report(name, country_id)
             SELECT 'Tax Report - ' || c.name, l.country_id
               FROM account_tax_report_line l
               JOIN res_country c ON c.id = l.country_id
              WHERE l.report_id IS NULL
                AND l.parent_id IS NULL
                AND NOT EXISTS (SELECT 1 FROM account_tax_report WHERE country_id = l.country_id)
           GROUP BY l.country_id, c.name
        """
    )
    cr.execute(
        """
        UPDATE account_tax_report_line l
           SET report_id = r.id
          FROM account_tax_report r
         WHERE r.country_id = l.country_id
           AND l.report_id IS NULL
           AND l.parent_id IS NULL
        """
    )
    # Assume the parent has the same country.
    cr.execute(
        r"""
        UPDATE account_tax_report_line l
           SET report_id = p.report_id
          FROM account_tax_report_line p
         WHERE l.report_id IS NULL
           AND p.id = (regexp_match(l.parent_path, '(\d+)/'))[1]::integer
        """
    )

    util.remove_column(cr, "account_tax_report_line", "country_id")
