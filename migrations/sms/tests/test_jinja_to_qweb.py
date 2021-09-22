# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

jinja_content = r"""
<p>a${'b' or '' | safe} !<a href="${ 'c' or '' | safe }">d</a> e ${'f' or '' | safe}<br>g</p>
""".strip()

inline_template_content = r"""
<p>a{{ 'b' or '' }} !<a href="{{ 'c' or '' }}">d</a> e {{ 'f' or '' }}<br>g</p>
""".strip()


@change_version("saas~14.5")
class CheckJinjaToQweb(UpgradeCase):
    def prepare(self):
        model_id = self.env["ir.model"]._get_id("res.partner")
        template = self.env["sms.template"].create(
            {
                "name": "jinja to inline",
                "model_id": model_id,
                "body": jinja_content,
                "lang": jinja_content,
            }
        )
        return {"template_id": template.ids}

    def check(self, init):
        template = self.env["sms.template"].browse(init["template_id"])
        inline_fields = [
            "body",
            "lang",
        ]
        for field in inline_fields:
            self.assertEqual(inline_template_content, template[field])
