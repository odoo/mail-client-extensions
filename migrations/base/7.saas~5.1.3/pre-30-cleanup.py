# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from lxml import etree


def migrate(cr, version):
    # this views is auto-generated when updating res.groups
    util.remove_record(cr, 'base.user_groups_view')

    # this view contains deleted fields (gmail_user, ...)
    util.remove_record(cr, 'base.view_users_form')

    # specific 'accounts':
    cr.execute("select value from ir_config_parameter where key = 'database.uuid'")
    dbuuid, = cr.fetchone()
    if dbuuid == '8851207e-1ff9-11e0-a147-001cc0f2115e':
        # these views prevents updating the modules:
        util.remove_record(cr, 'website.editor_head')
        util.remove_record(cr, 'report.html_container')
        util.remove_record(cr, 'base.view_module_filter')

        # cannot delete this view (noupdate='t'), that's why it's commented:
        #util.remove_record(cr, 'website.footer_custom')

        # calendar event: renamed fields but they are used in a custom view (calendar_ps):
        cr.execute("select arch from ir_ui_view where id = 2789")
        arch_data, = cr.fetchone()
        arch = etree.fromstring(arch_data)
        calendar = arch.xpath('//calendar')[0]
        calendar.attrib['date_start'] = 'start_datetime'
        calendar.attrib['date_stop'] = 'stop_datetime'
        new_arch = etree.tostring(arch)
        cr.execute("update ir_ui_view set arch = %s where id = 2789", [new_arch])

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

