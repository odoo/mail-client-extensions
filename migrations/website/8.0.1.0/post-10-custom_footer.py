# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from lxml import etree


def migrate(cr, version):
    cr.execute("select res_id, noupdate from ir_model_data where name = 'footer_custom' and module = 'website'")
    footer_custom_view_id, noupdate = cr.fetchone()
    if noupdate:
        footer_default_view_id = util.ref(cr, 'website.footer_default')
        cr.execute(
            "select arch from ir_ui_view where id = %s",
            [footer_default_view_id]
        )
        arch_data, = cr.fetchone()
        arch = etree.fromstring(arch_data)
        data = arch.xpath('//data')
        if data:
            d = data[0]
            d.attrib['optional'] = 'disabled'
            new_arch = etree.tostring(arch)
            cr.execute(
                "update ir_ui_view set arch = %s where id = %s",
                [new_arch, footer_default_view_id])

