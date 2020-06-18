# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "crm_iap_lead.enrich_service_information", "crm_iap_lead.enrich_company")
