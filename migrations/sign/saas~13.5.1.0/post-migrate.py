# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    env.ref("sign.group_sign_user").write(
        {
            "implied_ids": [
                (3, env.ref("base.group_user").id),
                (4, env.ref("sign.group_sign_employee").id),
            ],
        }
    )
