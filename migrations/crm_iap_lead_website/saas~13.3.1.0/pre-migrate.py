# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE "crm_lead_tag_crm_reveal_rule_rel"
        RENAME TO   "crm_reveal_rule_crm_tag_rel"
        """
    )

    cr.execute(
        """
        ALTER TABLE   "crm_reveal_rule_crm_tag_rel"
        RENAME COLUMN "crm_lead_tag_id"
        TO            "crm_tag_id"
        """
    )
