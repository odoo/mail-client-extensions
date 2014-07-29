# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from lxml import etree


def migrate(cr, version):
    # this views is auto-generated when updating res.groups
    util.remove_record(cr, 'base.user_groups_view')

    # this view contains deleted fields (gmail_user, ...)
    util.remove_record(cr, 'base.view_users_form')

    # calendar event: some fields were renamed but they are used in a some views
    cr.execute("select id, arch from ir_ui_view where model = 'calendar.event'")
    views = cr.fetchall()

    map_fields = {
        'date': 'start_datetime',
        'date_deadline': 'stop_datetime',
    }

    for view_id, view_arch in views:
        arch = etree.fromstring(view_arch)
        root_tags = arch.xpath('//calendar|//gantt')
        changed = False
        for tag in root_tags:
            for attr in ('date_start', 'date_stop'):
                val = tag.attrib.get(attr)
                new_val = map_fields.get(val)
                if new_val:
                    changed = True
                    tag.attrib[attr] = new_val

        if changed:
            new_arch = etree.tostring(arch)
            cr.execute("update ir_ui_view set arch = %s where id = %s", [new_arch, view_id])

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

