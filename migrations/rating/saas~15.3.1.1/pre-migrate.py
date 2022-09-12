# -*- coding: utf-8 -*-

import re

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "rating.parent.mixin", "rating_last_value")

    util.rename_xmlid(cr, "rating.rating_rating_view", "rating.rating_rating_action")
    util.rename_xmlid(cr, "im_livechat.rating_rating_view_form_livechat", "rating.rating_rating_view_form_text")
    util.rename_xmlid(
        cr, "website_slides.rating_rating_view_kanban_slide_channel", "rating.rating_rating_view_kanban_stars"
    )
    util.update_record_from_xml(cr, "rating.rating_rating_view_kanban_stars")

    # adapt mail templates (and their translations) from method renaming
    fields_toupdate = [
        "email_cc",
        "email_from",
        "email_to",
        "lang",
        "partner_to",
    ]
    translated_fields_toupdate = [
        "body_html",
        "report_name",
        "subject",
    ]
    jsonb_column = util.column_type(cr, "mail_template", "body_html") == "jsonb"
    for old, new in [
        ("rating_get_rated_partner_id", "_rating_get_operator"),
        ("rating_get_partner_id", "_rating_get_partner"),
        ("rating_get_access_token", "_rating_get_access_token"),
    ]:
        re_old = r"\y" + re.escape(f"object.{old}()")
        re_new = f"object.{new}()"
        # from saas~15.5 we use jsonb for translated fields
        cr.execute(
            """
            UPDATE mail_template
               SET %s
             WHERE %s
            """
            % (
                ",\n".join(
                    [
                        ",\n".join(
                            f"{fname} = regexp_replace({fname}, %(old)s, %(new)s, 'g')" for fname in fields_toupdate
                        ),
                        ",\n".join(
                            f"{fname} = jsonb_build_object('en_US', regexp_replace({fname}->>'en_US', %(old)s, %(new)s, 'g'))"
                            if jsonb_column
                            else f"{fname} = regexp_replace({fname}, %(old)s, %(new)s, 'g')"
                            for fname in translated_fields_toupdate
                        ),
                    ]
                ),
                " OR ".join(
                    [
                        " OR ".join(f"{fname} ~ %(old)s" for fname in fields_toupdate),
                        " OR ".join(
                            f"{fname}->>'en_US' ~ %(old)s" if jsonb_column else f"{fname} ~ %(old)s"
                            for fname in translated_fields_toupdate
                        ),
                    ]
                ),
            ),
            {"old": re_old, "new": re_new},
        )
        cr.execute(
            """
            UPDATE ir_translation
               SET value = regexp_replace(value, %s, %s, 'g')
             WHERE name IN %s
               AND value ~ %s
            """,
            [re_old, re_new, tuple(f"mail.template,{fname}" for fname in fields_toupdate), re_old],
        )
