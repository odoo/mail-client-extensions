# -*- coding: utf-8 -*-
from concurrent.futures import ProcessPoolExecutor

from psycopg2.extras import execute_batch

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    cr.execute(
        """
        WITH partner_country AS (
            SELECT p.id,
                   COALESCE(c.id, comp_c.id, main_comp_c.id) as country_id

              FROM res_partner p
         LEFT JOIN res_country c ON c.id = p.country_id

         LEFT JOIN res_company comp ON comp.id = p.company_id
              JOIN res_partner comp_p ON comp_p.id = comp.partner_id
         LEFT JOIN res_country comp_c ON comp_c.id = comp_p.country_id

              JOIN res_company main_comp ON main_comp.id = %s
              JOIN res_partner main_comp_p ON main_comp_p.id = main_comp.partner_id
         LEFT JOIN res_country main_comp_c ON main_comp_c.id = main_comp_p.country_id

        )

        SELECT p.id,
               trim(COALESCE(p.mobile, p.phone)) as phone,
               c.code,
               c.phone_code
          FROM res_partner p
          JOIN partner_country r ON r.id = p.id
     LEFT JOIN res_country c ON c.id = r.country_id
         WHERE p.phone_sanitized IS NULL
           AND length(trim(COALESCE(p.mobile, p.phone))) > 3
    """,
        [util.ref(cr, "base.main_company")],
    )

    # NOTE
    # `ProcessPoolExecutor.map` arguments needs to be pickleable
    # Functions can only be pickle if they are importable.
    # However, the current file is not importable due to the dash in the filename.
    # We should then put the executed function in its own importable file.
    san = util.import_script("sms/saas~12.5.2.0/sanitize.py")

    with ProcessPoolExecutor() as executor:
        execute_batch(
            cr._obj,
            "UPDATE res_partner SET phone_sanitized = %s WHERE id = %s",
            executor.map(san.sanitize, *zip(*cr.fetchall())),
        )
