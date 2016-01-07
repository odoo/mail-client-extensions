# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    pre = util.import_script('event/8.saas~6.0.1/pre-20-keep-template.py')
    tid, modified = pre.get_template(cr)
    if not modified:
        nid = util.ref(cr, 'event.event_subscription')
        util.replace_record_references(cr, ('mail.template', tid), ('mail.template', nid))
