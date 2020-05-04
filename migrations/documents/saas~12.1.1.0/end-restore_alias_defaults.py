# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    shares = env["documents.share"].search([])

    for share in shares:
        share.update_alias_defaults()
