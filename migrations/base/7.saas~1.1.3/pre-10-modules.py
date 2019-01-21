# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "im", deps={"base"})
    util.new_module(cr, "im_livechat", deps={"im", "mail", "portal_anonymous"})
