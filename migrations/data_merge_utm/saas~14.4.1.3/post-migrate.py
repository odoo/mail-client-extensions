# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    models_to_enable = ["utm.campaign", "utm.medium", "utm.source"]
    env["ir.model"].search([("model", "in", models_to_enable)]).action_merge_contextual_enable()
