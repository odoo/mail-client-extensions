import sys
import uuid
from concurrent.futures import ProcessPoolExecutor

from psycopg2.extras import execute_batch

from odoo.upgrade import util


def migrate(cr, version):
    # calculating "phone_sanitized" is kind of complicated. Here's what we do:
    # 1. We choose which phone number to use in the same order as they would be considered
    # 2. We check if a "country_id" is entered, if not, default to the base company's "country_id"
    # 3. Skip over rows where a "phone_sanitized" value already exists just in case
    # 4. Skip over rows based on "phone_state" = 'incorrect' because this value helps us skip invalid numbers
    #    which would otherwise have their raw invalid numbers incorrectly populate the "phone_sanitized" column
    #    via this script
    # 5. Pass resulting values into external function to get final values and write these to the column
    cr.execute(
        """
        WITH lead AS (
            SELECT l.id,
                trim(COALESCE(l.mobile, l.phone)) as phone,
                COALESCE(l.country_id, r.country_id) AS country_id,
                %s AS company_id
            FROM crm_lead l
            JOIN res_company comp ON comp.id = l.company_id
            JOIN res_partner r ON comp.partner_id = r.id
            WHERE l.phone_sanitized IS NULL
                AND l.phone_state = 'correct'
                AND length(trim(COALESCE(l.mobile, l.phone))) > 3
        )
        SELECT l.id,
            l.phone,
            c.code,
            c.phone_code
        FROM lead l
            JOIN res_country c ON l.country_id = c.id
    """,
        [util.ref(cr, "base.main_company")],
    )

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
            "UPDATE crm_lead SET phone_sanitized = %s WHERE id = %s",
            executor.map(san.sanitize, *zip(*cr.fetchall()), chunksize=chunksize),
            page_size=chunksize,
        )
