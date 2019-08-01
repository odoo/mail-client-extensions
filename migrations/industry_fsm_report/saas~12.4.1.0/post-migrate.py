# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.env(cr)["project.worksheet.template"].search([])._generate_qweb_report_template()
