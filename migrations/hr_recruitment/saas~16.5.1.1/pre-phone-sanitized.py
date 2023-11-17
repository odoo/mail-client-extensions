# -*- coding: utf-8 -*-
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor

from psycopg2.extras import Json

from odoo.upgrade import util


def sanitize_fields(cr, san, phone_to_sanitize, phone_sanitized):
    cr.execute(
        f"""
        WITH applicant AS (
           SELECT a.id,
        trim(a.{phone_to_sanitize}) as phone,
        COALESCE( r_a.country_id , r.country_id) AS country_id,
        a.company_id AS company_id
      FROM hr_applicant a
      JOIN res_company comp ON comp.id = a.company_id
      JOIN res_partner r ON comp.partner_id = r.id
      JOIN res_partner r_a ON a.partner_id = r_a.id
     WHERE a.{phone_sanitized} IS NULL
       AND length(trim(a.{phone_to_sanitize})) > 3
    )
    SELECT a.id,
        a.phone,
        c.code,
        c.phone_code
    FROM applicant a
        JOIN res_country c ON a.country_id = c.id
    """
    )

    data = cr.fetchall()
    queries = []

    with ThreadPoolExecutor() as executor:
        for batch in util.chunks(executor.map(san.sanitize, *zip(*data)), size=256):
            values = {aid: phone for phone, aid in batch}
            queries.append(
                cr.mogrify(
                    f"UPDATE hr_applicant SET {phone_sanitized} = %s::jsonb->id::text WHERE id IN %s",
                    [Json(values), tuple(values)],
                ).decode()
            )

    util.parallel_execute(cr, queries)


def migrate(cr, version):
    # NOTE
    # `ProcessPoolExecutor.map` arguments needs to be pickleable
    # Functions can only be pickle if they are importable.
    # However, the current file is not importable due to the dash in the filename.
    # We should then put the executed function in its own importable file.
    name = f"_upgrade_{uuid.uuid4().hex}"
    san = sys.modules[name] = util.import_script("sms/saas~12.5.2.0/sanitize.py", name=name)

    util.create_column(cr, "hr_applicant", "partner_phone_sanitized", "varchar")
    sanitize_fields(cr, san, "partner_phone", "partner_phone_sanitized")

    util.create_column(cr, "hr_applicant", "partner_mobile_sanitized", "varchar")
    sanitize_fields(cr, san, "partner_mobile", "partner_mobile_sanitized")
