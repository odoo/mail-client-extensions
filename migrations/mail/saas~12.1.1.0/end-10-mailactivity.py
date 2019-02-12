# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    mixin = env['mail.activity.mixin']
    names = tuple(name for name, model in env.items() if issubclass(type(model), type(mixin)))
    cr.execute("UPDATE ir_model SET is_mail_activity=TRUE WHERE model IN %s", [names])
