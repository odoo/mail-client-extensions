# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    if not util.version_gte("16.0"):
        env["res.company"].search([])._create_default_project_documents_folder()
