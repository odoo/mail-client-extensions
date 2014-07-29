# -*- coding: utf-8 -*-

# specific changes per db...

from lxml import etree
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # it seems this xmlid has been added manually to the database, but wrongly
    cr.execute("UPDATE ir_model_data SET model=%s WHERE id=%s", ('ir.model.access', 920255))

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


def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key=%s", ('database.uuid',))
    [uuid] = cr.fetchone()
    noop = lambda *a: None
    {
        '05a64ced-5b98-488d-a833-a994f9b1dd80': _db_openerp,    # test
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,    # prod
    }.get(uuid, noop)(cr, version)
