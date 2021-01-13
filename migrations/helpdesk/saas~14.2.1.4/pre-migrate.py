# -*- coding: utf-8 -*-

from odoo.upgrade import util

def migrate(cr, version):
    util.create_m2m(cr, "helpdesk_sla_res_partner_rel", "helpdesk_sla", "res_partner")
