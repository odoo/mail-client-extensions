# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

jinja_content = r"""
<p>a${'b' or '' | safe} !<a href="${ 'c' or '' | safe }">d</a> e ${'f' or '' | safe}<br>g</p>
""".strip()

inline_template_content = r"""
<p>a{{ 'b' or '' }} !<a href="{{ 'c' or '' }}">d</a> e {{ 'f' or '' }}<br>g</p>
""".strip()

qweb_content = r"""
<p>a<t t-out="'b' or ''"></t> !<a t-attf-href="{{ 'c' or '' }}">d</a> e <t t-out="'f' or ''"></t><br>g</p>
""".strip()


@change_version("saas~14.5")
class CheckJinjaToQweb(UpgradeCase):
    def prepare(self):
        model_id = self.env["ir.model"]._get_id("res.partner")
        template = self.env["mailing.mailing"].create(
            {
                "mailing_model_id": model_id,
                "subject": jinja_content,
                "preview": jinja_content,
                "email_from": jinja_content,
                "reply_to": jinja_content,
                "lang": jinja_content,
                "body_arch": jinja_content,
                "body_html": jinja_content,
            }
        )
        return {"record_id": template.ids}

    def check(self, init):
        template = self.env["mailing.mailing"].browse(init["record_id"])
        inline_fields = [
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
        for field in inline_fields:
            self.assertEqual(inline_template_content, template[field])

        for field in qweb_fields:
            self.assertEqual(qweb_content, template[field])
