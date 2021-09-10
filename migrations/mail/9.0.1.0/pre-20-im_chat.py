# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "im_chat.conversation_state")
    util.remove_model(cr, "im_chat.session", drop_table=False)
    util.remove_model(cr, "im_chat.message", drop_table=False)
    util.remove_model(cr, "im_chat.presence")
