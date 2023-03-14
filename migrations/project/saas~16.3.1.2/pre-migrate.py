# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.adapt_domains(cr, "project.project", "commercial_partner_id", "partner_id.commercial_partner_id")
    util.remove_field(cr, "project.project", "commercial_partner_id")

    util.adapt_domains(cr, "project.task", "commercial_partner_id", "partner_id.commercial_partner_id")
    util.remove_field(cr, "project.task", "commercial_partner_id")

    util.adapt_domains(cr, "project.task", "project_color", "project_id.color")
    util.remove_field(cr, "project.task", "project_color")
