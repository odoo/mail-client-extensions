# -*- coding: utf-8 -*-

from odoo.upgrade import util
from odoo.upgrade.util.jinja_to_qweb import upgrade_jinja_fields


def migrate(cr, version):
    util.update_record_from_xml(cr, "planning.email_template_slot_single")
    util.update_record_from_xml(cr, "planning.email_template_planning_planning")

    inline_template_fields = [
        "subject",
        "preview",
        "email_from",
        "reply_to",
        "lang",
    ]
    qweb_fields = [
        "body_arch",
        "body_html",
    ]
    upgrade_jinja_fields(
        cr,
        "mailing_mailing",
        inline_template_fields,
        qweb_fields,
        name_field="subject",
        table_model_name="mailing_model_id",
        fetch_model_name=True,
    )
