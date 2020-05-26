# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    imp = util.import_script("base/12.0.1.3/post-only-one-user-type-group.py")
    imp.one_user_type_group(cr, [1, util.guess_admin_id(cr)])
