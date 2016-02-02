# -*- coding: utf-8 -*-
from lxml import etree
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'report.layout', False)
    for x in 'external internal minimal'.split():
        util.force_noupdate(cr, 'report.%s_layout' % x, False)

    # XXX should we just force update?
    with util.skippable_cm(), util.edit_view(cr, 'report.external_layout_header') as arch:
        node = arch.find('.//div[@t-field="company.partner_id"]/..')
        if node:
            node.attrib['name'] = 'company_address'
        else:
            node = arch.find('./div')
            etree.SubElement(node, 'div', name='company_address')

    with util.skippable_cm(), util.edit_view(cr, 'report.external_layout_footer') as arch:
        new_node = etree.fromstring("""
            <ul t-if="not company.custom_footer" class="list-inline" name="financial_infos">
                <li t-if="company.vat">TIN: <span t-field="company.vat"/></li>
            </ul>
        """)
        node = arch.find('.//ul')
        if node:
            node.addnext(new_node)
        else:
            node = arch.find('./div')
            node.append(new_node)
