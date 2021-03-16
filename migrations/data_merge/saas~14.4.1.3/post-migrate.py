# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    models_to_enable = [
        "res.country",
        "res.country.state",
        "res.partner.category",
        "res.partner.industry",
        "res.partner.title",
    ]
    env["ir.model"].search([("model", "in", models_to_enable)]).action_merge_contextual_enable()
