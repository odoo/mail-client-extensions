# -*- coding: utf-8 -*-
import os

from openerp.tools import ustr
from openerp.tools.misc import str2bool

from openerp.addons.base.maintenance.migrations import util


def is_saas(cr):
    """Return whether the current installation has saas modules installed or not"""
    # this is shitty, I know - but ¯\_(ツ)_/¯
    cr.execute("SELECT true FROM ir_module_module WHERE name like 'saas_%' AND state='installed'")
    return bool(cr.fetchone())


def migrate(cr, version):
    strict = str2bool(os.environ.get("ODOO_MIG_STRICT_CUSTOM_VIEWS_VALIDATION"), default=False)
    if not strict or util.ENVIRON.get("custom_views_valid") or not is_saas(cr):
        return

    env = util.env(cr)
    View = env["ir.ui.view"]
    try:
        for model in env.registry:
            if not View._validate_custom_views(model):
                # in 9.0, method return a boolean. In 10.0, an exception is raise directly.
                raise ValueError
    except ValueError as e:
        raise util.MigrationError("Invalid custom view(s) for model %s: %s" % (model, ustr(e)))

    util.ENVIRON["custom_views_valid"] = True
