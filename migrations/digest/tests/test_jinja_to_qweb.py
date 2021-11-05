# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

jinja_content = r"""
<p>a${'b' or '' | safe} !<a href="${ 'c' or '' }">d</a> e ${'f' or '' | safe}<br>g</p>
""".strip()

qweb_content = r"""
<p>a<t t-out="'b' or ''"/> !<a t-attf-href="{{ 'c' or '' }}">d</a> e <t t-out="'f' or ''"/><br/>g</p>
""".strip()


@change_version("saas~14.5")
class CheckJinjaToQweb(UpgradeCase):
    def prepare(self):
        template = self.env["digest.tip"].create(
            {
                "name": "jinja to inline",
                "tip_description": jinja_content,
            }
        )
        return {"record_id": template.ids}

    def check(self, init):
        template = self.env["digest.tip"].browse(init["record_id"])
        self.assertEqual(qweb_content, template["tip_description"])
