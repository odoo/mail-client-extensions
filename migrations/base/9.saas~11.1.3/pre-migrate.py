# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("DROP TABLE ir_autovacuum")   # should always have been a abstract model
