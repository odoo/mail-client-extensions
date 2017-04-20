# -*- coding: utf-8 -*-
import os
from odoo.tools import ustr
from odoo.tools.misc import str2bool
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not str2bool(os.environ.get('ODOO_MIG_STRICT_CUSTOM_VIEWS_VALIDATION'), default='on') or \
       util.ENVIRON.get('custom_views_valid'):
        return

    env = util.env(cr)
    View = env['ir.ui.view']
    try:
        for model in env.registry:
            if not View._validate_custom_views(model):
                # in 9.0, method return a boolean. In 10.0, an exception is raise directly.
                raise ValueError
    except ValueError as e:
        raise util.MigrationError('Invalid custom view(s) for model %s: %s' % (model, ustr(e)))

    util.ENVIRON['custom_views_valid'] = True
