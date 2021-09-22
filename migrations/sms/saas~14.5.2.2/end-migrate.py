# -*- coding: utf-8 -*-

from odoo.upgrade.util.jinja_to_qweb import upgrade_jinja_fields


def migrate(cr, version):
    inline_template_fields = [
        "name",
        "body",
        "lang",
    ]
    upgrade_jinja_fields(cr, "sms_template", inline_template_fields, [])
