# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    env["res.company"].search([])._create_default_project_documents_folder()
