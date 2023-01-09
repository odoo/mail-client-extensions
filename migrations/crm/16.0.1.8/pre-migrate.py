# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "crm_team", "lead_properties_definition", "jsonb")
    util.create_column(cr, "crm_lead", "lead_properties", "jsonb")
