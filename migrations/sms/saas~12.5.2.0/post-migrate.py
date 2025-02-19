import sys
import uuid
from concurrent.futures import ProcessPoolExecutor

from psycopg2 import sql
from psycopg2.extras import execute_batch

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    limit = 10**5
    there_is_moar = True
    partner_has_mobile = util.column_exists(cr, "res_partner", "mobile")  # field was removed in saas~18.2
    phone = "COALESCE(p.mobile, p.phone)" if partner_has_mobile else "p.phone"
    while there_is_moar:
        cr.execute(
            util.format_query(
                cr,
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
                    trim({phone}) as phone,
                    c.code,
                    c.phone_code
                  FROM res_partner p
                  JOIN partner_country r ON r.id = p.id
             LEFT JOIN res_country c ON c.id = r.country_id
                 WHERE p.phone_sanitized IS NULL
                   AND length(trim({phone})) > 3
                 LIMIT %s
                """,
                phone=sql.SQL(phone),
            ),
            [util.ref(cr, "base.main_company"), limit],
        )
        if cr.rowcount < limit:
            there_is_moar = False

        # NOTE
        # `ProcessPoolExecutor.map` arguments needs to be pickleable
        # Functions can only be pickle if they are importable.
        # However, the current file is not importable due to the dash in the filename.
        # We should then put the executed function in its own importable file.
        name = f"_upgrade_{uuid.uuid4().hex}"
        san = sys.modules[name] = util.import_script("sms/saas~12.5.2.0/sanitize.py", name=name)

        with ProcessPoolExecutor() as executor:
            chunksize = 1024
            execute_batch(
                cr._obj,
                "UPDATE res_partner SET phone_sanitized = %s WHERE id = %s",
                executor.map(san.sanitize, *zip(*cr.fetchall()), chunksize=chunksize),
                page_size=chunksize,
            )
