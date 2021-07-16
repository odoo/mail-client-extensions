# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    fil = util.ref(cr, "base.lang_fil")
    tl = util.ref(cr, "base.lang_tl")
    if fil and tl:
        util.replace_record_references(cr, ("res.lang", fil), ("res.lang", tl), replace_xmlid=False)

    # avoid translation constraints
    # "ir_translation_code_unique" UNIQUE, btree (type, lang, md5(src)) WHERE type::text = 'code'::text
    # "ir_translation_model_unique" UNIQUE, btree (type, lang, name, res_id) WHERE type::text = 'model'::text
    # "ir_translation_unique" UNIQUE, btree (type, name, lang, res_id, md5(src))
    # https://github.com/odoo/odoo/blob/ad421baf18e7149e12f52869235ee653a6235f6e/odoo/addons/base/models/ir_translation.py#L193-L198
    cr.execute(
        """
        WITH dup AS (
            SELECT fil.id
              FROM ir_translation fil
              JOIN ir_translation tl
                ON -- ir_translation_code_unique
                    (    fil.type = 'code'
                     AND  tl.type = 'code'
                     AND md5(fil.src) = md5(tl.src)
                    )
                OR -- ir_translation_model_unique
                    (    fil.type = 'model'
                     AND  tl.type = 'model'
                     AND fil.name = tl.name
                     AND fil.res_id = tl.res_id
                    )
                OR -- ir_translation_unique
                    (    fil.type = tl.type
                     AND fil.name = tl.name
                     AND fil.res_id = tl.res_id
                     AND md5(fil.src) = md5(tl.src)
                    )

             WHERE fil.lang = 'fil_PH'
               AND tl.lang = 'tl_PH'
            )
        DELETE FROM ir_translation tr
              USING dup
              WHERE tr.id=dup.id
        """
    )
    cr.execute("UPDATE ir_translation SET lang = 'tl_PH' WHERE lang = 'fil_PH'")
    cr.execute("UPDATE res_partner SET lang = 'tl_PH' WHERE lang = 'fil_PH'")
    util.remove_record(cr, "base.lang_fil")

    cr.execute(
        """
        DELETE FROM ir_act_window_group_rel
              WHERE act_id IN %s
                AND gid = %s
    """,
        [
            (util.ref(cr, "base.change_password_wizard_action"), util.ref(cr, "base.reset_view_arch_wizard_action")),
            util.ref(cr, "base.group_erp_manager"),
        ],
    )
