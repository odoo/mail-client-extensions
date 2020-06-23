# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    fil = util.ref(cr, "base.lang_fil")
    tl = util.ref(cr, "base.lang_tl")
    if fil and tl:
        util.replace_record_references(cr, ("res.lang", fil), ("res.lang", tl), replace_xmlid=False)
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
