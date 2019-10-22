# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("UPDATE uom_category SET measure_type = 'working_time' WHERE measure_type = 'time'")
