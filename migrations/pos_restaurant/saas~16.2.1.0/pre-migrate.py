# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "pos_config_restaurant_floor_rel", "restaurant_floor", "pos_config")
    cr.execute(
        """
            INSERT INTO pos_config_restaurant_floor_rel(restaurant_floor_id, pos_config_id)
                 SELECT id, pos_config_id
                   FROM restaurant_floor
                  WHERE pos_config_id IS NOT NULL
        """
    )
    util.remove_field(cr, "restaurant.floor", "pos_config_id")
