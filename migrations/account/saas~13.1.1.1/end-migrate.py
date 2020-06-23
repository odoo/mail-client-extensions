# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_tax_report", "_tmp", "int4")
    cr.execute(
        """
        WITH new_reports AS (
            INSERT INTO account_tax_report(name, country_id, _tmp)
                 SELECT name, country_id, id
                   FROM account_tax_report_line
                  WHERE report_id IS NULL
                    AND parent_id IS NULL
              RETURNING id, _tmp
        )
        UPDATE account_tax_report_line l
           SET report_id = n.id
          FROM new_reports n
         WHERE l.id = n._tmp
    """
    )
    cr.execute(
        r"""
        UPDATE account_tax_report_line l
           SET report_id = p.report_id
          FROM account_tax_report_line p
         WHERE l.report_id IS NULL
           AND p.id = (regexp_match(l.parent_path, '(\d+)/'))[1]::integer
    """
    )

    util.remove_column(cr, "account_tax_report", "_tmp")
    util.remove_column(cr, "account_tax_report_line", "country_id")
