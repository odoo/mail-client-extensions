# -*- coding: utf-8 -*-

from lxml import etree, html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")


def innerxml(element):
    return "".join(etree.tostring(child, encoding=str, method="html") for child in element)


@change_version("saas~17.2")
class TestEmbedCode(UpgradeCase):
    def prepare(self):
        inner_code = """
<script>
    document.addEventListener('DOMContentLoaded', function () {
    const alertEl = document.createElement('div');
    alertEl.classList.add('alert', 'alert-primary');
    alertEl.textContent = "Hello";
    document.getElementById('some-stuff').appendChild(alertEl);
    });
</script>
<div id="some-stuff"></div>
        """.replace(r"\n", "").strip()
        arch = f"""
<t name="Embed Code Snippet Test" t-name="website.embed_code_test">
    <t t-call="website.layout">
        <t t-set="pageName" t-value="'embed code test'"/>
        <div id="wrap" class="oe_structure oe_empty">
            <section class="s_embed_code text-center pt64 pb64 o_colored_level" data-snippet="s_embed_code" data-name="Embed Code">
                <div class="s_embed_code_embedded container o_not_editable" contenteditable="false">{inner_code}</div>
            </section>
            <section class="s_embed_code text-center pt64 pb64 o_colored_level" data-snippet="s_embed_code" data-name="Embed Code">
                <template class="s_embed_code_saved">{inner_code}</template>
                <div class="s_embed_code_embedded container o_not_editable" contenteditable="false">{inner_code}</div>
            </section>
        </div>
    </t>
</t>
        """
        view = self.env["ir.ui.view"].create(
            {
                "name": "Embed Code Snippet Test",
                "type": "qweb",
                "key": "website.embed_code_test",
                "website_id": self.env.ref("website.default_website").id,
                "arch": arch.replace(r"\n", ""),
            }
        )
        return {"view_id": view.id, "inner_code": inner_code}

    def check(self, init):
        arch = self.env["ir.ui.view"].browse(init["view_id"]).arch_db
        root_el = html.fromstring(f"<wrap>{arch}</wrap>", parser=utf8_parser)
        templates = root_el.xpath('.//template[hasclass("s_embed_code_saved")]')

        self.assertEqual(
            init["inner_code"],
            innerxml(templates[0]),
            "The full code should be in the created template element.",
        )
        self.assertEqual(2, len(templates), "The 2nd snippet shouldn't have created a second template.")
