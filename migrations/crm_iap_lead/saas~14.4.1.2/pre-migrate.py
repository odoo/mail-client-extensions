# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    module = "crm_iap_mine" if util.version_gte("saas~14.5") else "crm_iap_lead"

    util.create_column(cr, "crm_iap_lead_mining_request", "error_type", "varchar")
    cr.execute(
        """
        UPDATE crm_iap_lead_mining_request
           SET error_type = 'credits'
         WHERE state = 'error'
        """
    )
    util.remove_field(cr, "crm.iap.lead.mining.request", "error")

    util.rename_field(cr, "crm.iap.lead.industry", "reveal_id", "reveal_ids")
    util.create_column(cr, "crm_iap_lead_industry", "sequence", "int4")

    # industry data have been updated modified in CSV file

    # 1. update record references of merged industries
    industry_ids_to_merge = {
        "151": "150",
        "154": "153",
        "155": "30",
        "156": "138",
        "157": "69",
        "159": "158",
    }

    def ref(num):
        return util.ref(cr, f"{module}.crm_iap_lead_industry_{num}")

    mapping = {ref(old_id): ref(new_id) for old_id, new_id in industry_ids_to_merge.items()}
    mapping.pop(None, None)
    if mapping:
        util.replace_record_references_batch(
            cr,
            mapping,
            "crm.iap.lead.industry",
            replace_xmlid=False,
        )

    # 2. remove unused industries & merged ones
    industry_ids_to_remove = ["146", "151", "154", "155", "156", "157", "159", "164"]
    util.delete_unused(cr, *[f"{module}.crm_iap_lead_industry_{num}" for num in industry_ids_to_remove])

    # 3. rename the ones we keep with their new name (including multiple ids)
    prefix = "crm_iap_lead_industry"
    for pre, post in [
        ("30", "30_155"),
        ("69", "69_157"),
        ("138", "138_156"),
        ("150", "150_151"),
        ("153", "153_154"),
        ("158", "158_159"),
    ]:
        util.rename_xmlid(cr, f"{module}.{prefix}_{pre}", f"{module}.{prefix}_{post}")
