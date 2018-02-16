# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute(
        "UPDATE delivery_carrier SET usps_service='First Class' WHERE usps_service='First-Class'")
