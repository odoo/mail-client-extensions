# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~17.3", "18.0"):
        act_id = util.ref(cr, "knowledge.knowledge_article_action_form")
        cr.execute("UPDATE ir_act_window SET path=NULL WHERE id=%s", [act_id])
