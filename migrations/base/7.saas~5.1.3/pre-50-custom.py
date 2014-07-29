# -*- coding: utf-8 -*-
"""Custom scripts for specific databases (yuk)"""

from lxml import etree
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # specific 'accounts':
    cr.execute("select value from ir_config_parameter where key = 'database.uuid'")
    dbuuid, = cr.fetchone()
    if dbuuid in ('8851207e-1ff9-11e0-a147-001cc0f2115e', '05a64ced-5b98-488d-a833-a994f9b1dd80'):
        # these views prevents updating the modules:
        util.remove_record(cr, 'website.editor_head')
        util.remove_record(cr, 'report.html_container')
        util.remove_record(cr, 'base.view_module_filter')

        # select arch from ir_ui_view where name = 'openerp.salesmen.invoices.odo'
        cr.execute("select id, arch from ir_ui_view where name = %s", ['openerp.salesmen.invoices.odo'])
        view_id, arch_data = cr.fetchone()
        arch = etree.fromstring(arch_data)
        tag = arch.xpath("//button")[0]
        tag.tag = 'xpath'
        if 'string' in tag.attrib:
            del tag.attrib['string']
        tag.attrib['expr'] = "//button[@id='invoice_button']"
        new_arch = etree.tostring(arch)
        cr.execute("update ir_ui_view set arch = %s where id = %s", [new_arch, view_id])
