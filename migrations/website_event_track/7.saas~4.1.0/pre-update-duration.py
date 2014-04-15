# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""ALTER TABLE event_track
                    ALTER COLUMN duration TYPE numeric
                    USING duration::numeric/60
               """)
