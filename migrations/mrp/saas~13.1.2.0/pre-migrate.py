# -*- coding: utf-8 -*-


def migrate(cr, version):
    # beside the default value is `strict`, the code only compare the value to `strict`. This mean
    # that a NULL value has the same behavior as `flexible`
    cr.execute("UPDATE mrp_bom SET consumption = 'flexible' WHERE consumption IS NULL")
