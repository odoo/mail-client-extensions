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


@change_version("saas~14.5")
class JinjaToQweb_Data(UpgradeCase):
    """
    Force the tip `sms_template_demo_0` to be converted to QWeb via the upgrade script helpers
    """

    def _is_demo(self):
        self.env.cr.execute("SELECT demo FROM ir_module_module WHERE name='base'")
        return bool(self.env.cr.fetchone()[0])

    def prepare(self):
        if not self._is_demo():
            # runbot also test the upgrade without demo data
            return
        sms_id = self.env.ref("sms.sms_template_demo_0").id
        self.env.cr.execute(
            """
                UPDATE sms_template
                   SET create_date = create_date - interval '42 minutes'
                 WHERE id = %s
            """,
            [sms_id],
        )
        self.env.cr.execute(
            """
                UPDATE ir_translation
                   SET src = src || '$$', value = value || '$$'
                 WHERE name = 'sms.template,body'
                   AND res_id = %s
            """,
            [sms_id],
        )

    def check(self, _):
        if not self._is_demo():
            return
        sms = self.env.ref("sms.sms_template_demo_0")
        self.assertIn(r"{{", sms.body)

        # test translations have been updated.
        fr = sms.with_context(lang="fr_FR")
        self.assertIn(r"{{", fr.body)
        self.assertIn(r"$$", fr.body)
