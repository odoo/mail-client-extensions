# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE "crm_iap_lead_mining_request_crm_lead_tag_rel"
        RENAME TO   "crm_iap_lead_mining_request_crm_tag_rel"
        """)

    cr.execute(
        """
        ALTER TABLE   "crm_iap_lead_mining_request_crm_tag_rel"
        RENAME COLUMN "crm_lead_tag_id"
        TO            "crm_tag_id"
        """)
