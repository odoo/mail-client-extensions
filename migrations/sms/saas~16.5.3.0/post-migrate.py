from uuid import uuid4

from psycopg2.extras import execute_values

from odoo.upgrade import util


def migrate(cr, version):
    # Add uuids to outgoing sms and create sms_trackers for outgoing sms with notifications
    cr.execute("SELECT id FROM sms_sms WHERE state='outgoing'")
    sms_and_uuids = [(res[0], uuid4().hex) for res in cr.fetchall()]
    if sms_and_uuids:
        cr.execute(
            """
        CREATE TEMP TABLE uuids_sms_temp(
            id SERIAL PRIMARY KEY,
            uuid varchar(32))
        """
        )
        execute_values(cr._obj, "INSERT INTO uuids_sms_temp (id, uuid) VALUES %s", sms_and_uuids)
        cr.execute(
            """
            WITH sms_updated AS (
                UPDATE sms_sms s
                   SET uuid = u.uuid
                  FROM uuids_sms_temp u
                 WHERE s.id = u.id
            )
            INSERT INTO sms_tracker (sms_uuid, mail_notification_id)
                 SELECT u.uuid as sms_uuid,
                        n.id as mail_notification_id
                   FROM uuids_sms_temp u
                   JOIN mail_notification n
                     ON n.sms_id_int = u.id
            """,
        )
        # Same for traces
        if util.table_exists(cr, "mailing_trace") and util.column_exists(cr, "mailing_trace", "sms_id_int"):
            cr.execute(
                """
                INSERT INTO sms_tracker (sms_uuid, mailing_trace_id)
                     SELECT u.uuid as sms_uuid,
                            t.id as mailing_trace_id
                       FROM uuids_sms_temp u
                       JOIN mailing_trace t
                         ON t.sms_id_int = u.id
                      WHERE u.uuid IS NOT NULL
                """
            )
