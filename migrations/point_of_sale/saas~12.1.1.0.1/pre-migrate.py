# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.module_installed(cr, "hr"):
        # force creation of the new field (see odoo/odoo#28567) in case the `hr` module hasn't been loaded yet.
        util.create_column(cr, "hr_employee", "pin", "varchar")

        cr.execute(
            """
            UPDATE hr_employee emp
               SET pin = usr.pos_security_pin
              FROM res_users usr
             WHERE usr.id = emp.user_id
               AND emp.pin IS NULL
            """
        )

    util.remove_field(cr, "pos.config", "barcode_scanner")
    util.remove_field(cr, "res.users", "pos_security_pin")
    util.remove_view(cr, "point_of_sale.res_users_view_form")
    util.remove_view(cr, "point_of_sale.pos_config_view_form")
