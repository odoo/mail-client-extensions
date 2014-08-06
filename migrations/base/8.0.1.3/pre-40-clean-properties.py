# -*- coding: utf-8 -*-

def migrate(cr, version):
    # before 8.0, falsey properties mean "default property"
    # in 8.0, this mean "no value"
    cr.execute("""DELETE FROM ir_property
                        WHERE res_id IS NOT NULL
                          AND value_text IS NULL
                          AND value_float IS NULL
                          AND value_integer IS NULL
                          AND value_datetime IS NULL
                          AND value_binary IS NULL
                          AND value_reference IS NULL
               """)
