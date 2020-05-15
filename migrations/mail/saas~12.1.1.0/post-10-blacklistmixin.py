# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    mixin = "mail.thread.blacklist" if util.version_gte("saas~12.4") else "mail.blacklist.mixin"
    util.remove_inherit_from_model(cr, "mail.channel.partner", mixin)
