# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_config_parameter
           SET "key" = 'base_geolocalize.google_map_api_key'
         WHERE "key" = 'google.api_key_geocode'
    """)
