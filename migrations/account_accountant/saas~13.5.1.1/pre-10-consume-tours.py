# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO web_tour_tour(user_id, name)
            SELECT uid, unnest(ARRAY['account_accountant_tour_upload', 'account_accountant_tour_upload_ocr_step'])
            FROM res_groups_users_rel
            WHERE gid = %s
    """,
        [util.ref(cr, "base.group_erp_manager")],
    )
