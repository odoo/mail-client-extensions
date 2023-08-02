# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    arch = util.get_value_or_en_translation(cr, "ir_ui_view", "arch_db")
    cr.execute(
        r"""
            SELECT id
              FROM ir_ui_view
             WHERE key = 'website_helpdesk.team'
               AND website_id IS NOT NULL
               AND {arch} LIKE '%t-value="len(teams)&gt;1"%'
        """.format(
            arch=arch
        )
    )
    for (view,) in cr.fetchall():
        with util.edit_view(cr, view_id=view) as arch:
            for node in arch.xpath('//t[@t-set="many_teams"]'):
                parent = node.getparent()
                parent.getparent().remove(parent)

            div = util.lxml.etree.Element("div", {"t-if": "team.use_website_helpdesk_form"})
            t_1 = util.lxml.etree.Element(
                "t", {"t-set": "template_xmlid", "t-value": "team.website_form_view_id.xml_id"}
            )
            t_2 = util.lxml.etree.Element("t", {"t-call": "#{template_xmlid}"})
            div.extend([t_1, t_2])
            for node in arch.xpath('//div[@id="website_helpdesk_form"]'):
                node.addnext(div)
                node.getparent().remove(node)

            for node in arch.xpath('//t[@t-if="team.use_website_helpdesk_form"]'):
                node.getparent().remove(node)
            for node in arch.xpath('//div[@id="oe_structure_website_helpdesk_links"]'):
                node.getparent().remove(node)
