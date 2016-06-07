# -*- coding: utf-8 -*-
from openerp.modules.module import get_module_resource
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    with open(get_module_resource('web', 'static', 'src', 'img', 'favicon.ico')) as fp:
        icon = fp.read()

    util.env(cr)['website'].with_context(active_test=False).search([], limit=None).write({
        'favicon': icon.encode('base64'),
    })
