import sys
import uuid
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

from psycopg2.extras import execute_batch

from odoo.upgrade import util


def sanitize_and_update(cr):
    # We need to correct the phone_sanitized and the phone_state based on updated phone numbers.
    # phone_sanitized takes mobile first as candidate, then phone, when both are set and different
    # we must updated the sanitized number and state.
    # phone_state only uses 'phone' for status calculations, if we move mobile to phone we need to
    # recalculate phone_state based on *updated phone.
    cr.execute(
        """
        WITH lead AS (
            SELECT l.id,
                   TRIM(l.phone) AS phone,
                   COALESCE(l.country_id, r.country_id) AS country_id
              FROM crm_lead l
              JOIN res_company comp
                ON comp.id = COALESCE(l.company_id, %s)
              JOIN res_partner r
                ON comp.partner_id = r.id
             WHERE l._upg_phone_updated
        )
        SELECT l.id,
               l.phone,
               c.code,
               c.phone_code
          FROM lead l
          JOIN res_country c
            ON l.country_id = c.id
    """,
        [util.ref(cr, "base.main_company")],
    )

    name = f"_upgrade_{uuid.uuid4().hex}"
    san = sys.modules[name] = util.import_script("crm/saas~18.2.1.8/sanitize.py", name=name)

    with ProcessPoolExecutor(max_workers=util.get_max_workers(), mp_context=get_context("fork")) as executor:
        chunksize = 1024
        execute_batch(
            cr._obj,
            """
            UPDATE crm_lead
               SET phone_sanitized = %s,
                   phone_state = CASE WHEN %s THEN 'correct' ELSE 'incorrect' END
             WHERE id = %s
            """,
            executor.map(san.sanitize, *zip(*cr.fetchall()), chunksize=chunksize),
            page_size=chunksize,
        )


def migrate(cr, version):
    # Add the temporary tracking column
    util.create_column(cr, "crm_lead", "_upg_phone_updated", "boolean")

    query = cr.mogrify(
        """
        INSERT INTO mail_message (
                    res_id, model, author_id, message_type,
                    body, date)
             SELECT id, 'crm.lead', %s, 'notification',
                    'Previous Mobile: ' || mobile, NOW() at time zone 'UTC'
               FROM crm_lead
                 -- notify if both are set and different
              WHERE phone != mobile
        """,
        [util.ref(cr, "base.partner_root")],
    ).decode()

    util.explode_execute(cr, query, table="crm_lead")

    query = """
        UPDATE crm_lead
            -- flag if mobile is different from phone, including null phone
           SET _upg_phone_updated = phone IS DISTINCT FROM mobile,
            -- set the value only if phone is null
               phone = COALESCE(phone, mobile)
         WHERE mobile IS NOT NULL
    """
    util.explode_execute(cr, query, table="crm_lead")

    # Sanitize and recalculate phone_state based on updated phone
    sanitize_and_update(cr)

    util.remove_column(cr, "crm_lead", "_upg_phone_updated")

    util.remove_field(cr, "crm.lead", "mobile")
