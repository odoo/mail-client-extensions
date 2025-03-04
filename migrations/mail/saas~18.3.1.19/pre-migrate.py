from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail.mail_activity_type_form_inherit")
    cr.execute("""
    CREATE TABLE mail_message_link_preview(
        id SERIAL PRIMARY KEY,
        message_id integer NOT NULL,
        link_preview_id integer NOT NULL,
        sequence integer,
        is_hidden boolean,
        create_uid integer,
        write_uid integer,
        create_date timestamp without time zone,
        write_date timestamp without time zone
    )
    """)
    cr.execute("""
    WITH uniq_url AS (
        SELECT MAX(id) AS link_preview_id,
               source_url
          FROM mail_link_preview
      GROUP BY source_url
    ), _insert AS (
    INSERT INTO mail_message_link_preview (link_preview_id, message_id, is_hidden, create_uid, write_uid, create_date, write_date)
         SELECT u.link_preview_id,
                lp.message_id,
                lp.is_hidden,
                lp.create_uid,
                lp.write_uid,
                lp.create_date,
                lp.write_date
           FROM mail_link_preview AS lp
           JOIN uniq_url AS u
             ON u.source_url = lp.source_url
    )
    DELETE FROM mail_link_preview
          WHERE id NOT IN (SELECT link_preview_id FROM uniq_url)
    """)
    util.remove_field(cr, "mail.link.preview", "is_hidden")
    util.remove_field(cr, "mail.link.preview", "message_id")
    util.remove_field(cr, "mail.message", "link_preview_ids")

    util.move_field_to_module(cr, "res.users", "is_in_call", "im_livechat", "mail")
    util.create_column(cr, "discuss_channel_rtc_session", "partner_id", "integer")
    query = """
        UPDATE discuss_channel_rtc_session
           SET partner_id = m.partner_id
          FROM discuss_channel_member m
         WHERE channel_member_id = m.id
    """
    util.explode_execute(cr, query, "discuss_channel_rtc_session")

    util.remove_constraint(cr, "mail_activity", "mail_activity_check_res_id_is_set")

    util.remove_record(cr, "mail.module_category_canned_response")
