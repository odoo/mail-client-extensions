# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

jinja_content = r"""
<p>a${'b' or '' | safe or '' | safe} !<a href="${ 'c' or '' }">d</a> e ${'f' or '' | safe}<br>g</p>
""".strip()

# NOTE: inline templates are NOT parsed as xml, thus `<br>` stay as is.
inline_template_content = r"""
<p>a{{ 'b' or '' or '' }} !<a href="{{ 'c' or '' }}">d</a> e {{ 'f' or '' }}<br>g</p>
""".strip()

jinja_to_qweb_content = [
    {
        "before": r"""
% if True:
    <b>foo</b>
% endif
""",
        "after": r"""
<t t-if="True">
    <b>foo</b>
</t>
    """,
    },
    {
        "before": r"""
%if True:
    <b>foo</b>
% endif
""",
        "after": r"""
<t t-if="True">
    <b>foo</b>
</t>
    """,
    },
    {
        "before": r"""
% for foo in bar:
    <b>foo</b>
% endfor
""",
        "after": r"""
<t t-foreach="bar" t-as="foo">
    <b>foo</b>
</t>
    """,
    },
    {
        "before": r"""
%for foo in bar:
    <b>foo</b>
% endfor
""",
        "after": r"""
<t t-foreach="bar" t-as="foo">
    <b>foo</b>
</t>
    """,
    },
    {
        "before": r"""
<p>a${'b' or '' | safe} !<a href="${ 'c' or '' | safe }">d</a> e ${'f' or '' | safe}<br>g</p>
<div>
  % set items = [False or 'one', ">"]
  % for item in items
    <li>${item}</li>
  % endfor
  % if 'A' == 'B':
    <b>foo1</b>
  % elif 'B' == 'C':
    <b>foo2</b>
  % else:
    <b>foo3</b>
  % endif

  %if a
    <b>a</b>
  %endif

  <div>
    % if True:
      true 1
  </div>
%endif
</div>
""",
        "after": r"""
<p>a<t t-out="'b' or ''"/> !<a t-attf-href="{{ 'c' or '' }}">d</a> e <t t-out="'f' or ''"/><br/>g</p>
<div>
  <t t-set="items" t-value="[False or 'one', &quot;&gt;&quot;]"/>
  <t t-foreach="items" t-as="item">
    <li><t t-out="item"/></li>
  </t>
  <t t-if="'A' == 'B'">
    <b>foo1</b>
  </t>
  <t t-elif="'B' == 'C'">
    <b>foo2</b>
  </t>
  <t t-else="">
    <b>foo3</b>
  </t>

  <t t-if="a">
    <b>a</b>
  </t>

  <div>
    <t t-if="True">
      true 1
  </t></div>

</div>
""",
    },
    {
        "before": r"<!-- commenting ${foo} code -->",
        "after": r'<!-- commenting <t t-out="foo"/> code -->',
    },
]


@change_version("saas~14.5")
class CheckJinjaToQweb(UpgradeCase):
    def prepare(self):
        model_id = self.env["ir.model"]._get_id("res.partner")
        inline_template = self.env["mail.template"].create(
            {
                "name": "jinja to inline",
                "model_id": model_id,
                "subject": jinja_content,
                "email_from": jinja_content,
                "email_to": jinja_content,
                "partner_to": jinja_content,
                "email_cc": jinja_content,
                "reply_to": jinja_content,
                "report_name": jinja_content,
                "scheduled_date": jinja_content,
                "body_html": jinja_content,
            }
        )
        mail_template_id = self.env["mail.template"].create(
            [
                {
                    "name": f"template qweb #{i}",
                    "model_id": model_id,
                    "subject": "x",
                    "email_from": "x",
                    "email_to": "x",
                    "partner_to": "x",
                    "email_cc": "x",
                    "reply_to": "x",
                    "report_name": "x",
                    "scheduled_date": "x",
                    "body_html": content["before"].strip(),
                }
                for content, i in zip(jinja_to_qweb_content, range(len(jinja_to_qweb_content)))
            ]
        )
        return {"template_ids": mail_template_id.ids + inline_template.ids}

    def check(self, init):
        templates = self.env["mail.template"].browse(init["template_ids"])
        inline_fields = [
            "subject",
            "email_from",
            "email_to",
            "partner_to",
            "email_cc",
            "reply_to",
            "report_name",
            "scheduled_date",
        ]
        self.assertEqual(len(jinja_to_qweb_content) + 1, len(templates))
        for field in inline_fields:
            self.assertEqual(inline_template_content, templates[-1][field])
        for content, template in zip(jinja_to_qweb_content, templates):
            self.assertEqual(content["after"].strip(), template["body_html"].strip())
