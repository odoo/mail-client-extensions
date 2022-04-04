# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("REINDEX TABLE ir_model_data")
