# -*- coding: utf-8 -*-
from odoo.upgrade import util


def replace_resize_class(cr, model):
    util.remove_field_metadata(cr, model, "cover_properties")
    table = util.table_of_model(cr, model)
    cr.execute(
        rf"""
            UPDATE "{table}"
               SET cover_properties = jsonb_set(
                       cover_properties :: jsonb,
                       ARRAY[ 'resize_class' ] :: text[],
                       to_jsonb(
                           COALESCE(
                               regexp_replace(
                                   cover_properties :: jsonb ->> 'resize_class',
                                   '\ycover_mid\y', 'o_half_screen_height'
                               ),
                               'o_half_screen_height'
                           )
                       )
                   )
             WHERE cover_properties IS NOT NULL
        """
    )
