# -*- coding: utf-8 -*-

import os

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "base_onboarding_company_state")

    cr.execute(
        """
        INSERT INTO res_partner_category(name, active)
        VALUES(jsonb_build_object('en_US', 'Old Private Address'), True)
        RETURNING id"""
    )
    [tag_id] = cr.fetchone()

    cr.execute(
        """
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
        VALUES ('base', 'res_partner_category_old_private_address', 'res.partner.category', %s, true)
        """,
        [tag_id],
    )

    cr.execute(
        """
        INSERT INTO res_partner_res_partner_category_rel(category_id, partner_id)
        SELECT %s, id
          FROM res_partner
         WHERE type = 'private'
    """,
        (tag_id,),
    )

    util.explode_execute(
        cr,
        """
        UPDATE res_partner
           SET name = COALESCE(name, '/'),
               active = false,
               type = 'contact'
         WHERE type = 'private'
        """,
        table="res_partner",
    )

    if util.str2bool(os.getenv("UPG_RECYCLE_PRIVATE_PARTNERS", "0")):
        rpp = util.import_script("base/saas~16.4.1.3/recycle_private_partners.py")
        rpp.recycle(util.env(cr), direct=True)
