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
    util.remove_view(cr, 'base.view_module_filter')

    bad_view_id = 2789
    cr.execute("SELECT arch from ir_ui_view where id=%s", (bad_view_id,))
    arch = etree.fromstring(cr.fetchone()[0])
    arch.attrib['date_start'] = 'start'
    arch.attrib['date_stop'] = 'stop'
    cr.execute("UPDATE ir_ui_view SET arch=%s WHERE id=%s", (etree.tostring(arch), bad_view_id))

def _feuerwear(cr, version):
    cr.execute("DELETE FROM ir_ui_view WHERE id = 1008")

def _osnet(cr, version):
    util.remove_view(cr, 'project_mrp.view_project_mrp_inherit_form2')
    util.remove_record(cr, 'sale_crm.account_invoice_groupby_inherit')

def _lajs(cr, version):
    website_aj_layout_view_id = util.ref(cr, 'website_aj.layout')
    cr.execute("select arch from ir_ui_view where id = %s", [website_aj_layout_view_id ])
    res = cr.fetchone()
    if res:
        body = etree.fromstring(res[0])
        wrap_search = body.xpath("//div[@id='wrapwrap']")
        if wrap_search:
            wrap_div = wrap_search[0]
            wrap_div.insert(1, etree.SubElement(wrap_div, 'header'))

            header = wrap_div.getchildren()[1]
            for child in wrap_div.getchildren():
                if child.tag not in ('header', 'footer'):
                    header.append(child)

            new_body = etree.tostring(body)
            cr.execute("update ir_ui_view set arch = %s where id = %s", [new_body, util.ref(cr, 'website_aj.layout')])

def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key=%s", ('database.uuid',))
    [uuid] = cr.fetchone()
    noop = lambda *a: None
    {
        '05a64ced-5b98-488d-a833-a994f9b1dd80': _db_openerp,    # test
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,    # prod
        '8b833269-2a1e-4495-a50c-978434fe4187': _feuerwear,     # feuerwear
        'ab9b66f4-7cd9-11e2-aa3a-000c29d0cefb': _osnet,
        'db5c0cb1-5bb3-46af-b15f-50bf67bec24b': _lajs,
    }.get(uuid, noop)(cr, version)

