# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("UPDATE event_event SET note='<pre>'||note||'</pre>'")
