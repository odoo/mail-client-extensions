# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        INSERT INTO quality_point_test_type(name, technical_name)
             SELECT initcap(_test_type), _test_type
               FROM quality_point
              WHERE _test_type NOT IN ('passfail', 'measure')
    """)
    cr.execute("""
        UPDATE quality_point p
           SET test_type_id = t.id
          FROM quality_point_test_type t
         WHERE p._test_type = t.technical_name
    """)
    cr.execute("ALTER TABLE quality_point ALTER COLUMN test_type_id SET NOT NULL")

    util.remove_column(cr, 'quality_point', '_test_type')
