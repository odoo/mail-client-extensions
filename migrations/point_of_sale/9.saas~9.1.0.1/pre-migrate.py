# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "pos_config")
    util.remove_view(cr, "point_of_sale.res_users_form_preference_view")
    util.remove_view(cr, "point_of_sale.res_users_form_view")
