# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "partner_autocomplete.enrich_service_information", "iap_mail.enrich_company")
