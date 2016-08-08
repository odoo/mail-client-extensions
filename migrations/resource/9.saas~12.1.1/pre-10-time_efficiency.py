# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("UPDATE resource_resource SET time_efficiency = time_efficiency * 100")
