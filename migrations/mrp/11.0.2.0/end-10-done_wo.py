# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Set done_wo fields
    cr.execute("""UPDATE stock_move_line ml SET done_wo='t' WHERE done_wo IS NULL""")
    cr.execute("""UPDATE stock_move_line ml SET production_id = CASE WHEN m.raw_material_production_id IS NOT NULL
                                                                    THEN m.raw_material_production_id
                                                                    ELSE m.production_id END
                    FROM stock_move m WHERE ml.move_id = m.id AND ml.production_id IS NULL
                        AND (m.production_id IS NOT NULL OR m.raw_material_production_id IS NOT NULL)""")