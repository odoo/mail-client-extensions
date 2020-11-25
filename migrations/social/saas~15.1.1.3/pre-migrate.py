# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "social_account", "name", "varchar")

    # copy name from related utm_medium
    cr.execute(
        """
        UPDATE social_account sa
           SET name = um.name
          FROM utm_medium um
         WHERE sa.utm_medium_id = um.id;
        """
    )

    util.remove_inherit_from_model(cr, "social.account", "utm.medium", keep={"name", "active"})
