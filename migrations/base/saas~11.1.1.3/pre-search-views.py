# -*- coding: utf-8 -*-
from itertools import count

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Since odoo/odoo@8f88c0336f881dd59d7c25b64c5bcba1989f998b, search views' filters MUST have
    # a `name` attribute. Force update of standard views. Change others.
    cr.execute(
        """
        WITH views AS (
            UPDATE ir_model_data
               SET noupdate = false
             WHERE model = 'ir.ui.view'
               AND COALESCE(module, '') NOT IN ('', '__export__')
               AND res_id IN (SELECT id FROM ir_ui_view WHERE type='search')
         RETURNING res_id
        )
        SELECT id
          FROM ir_ui_view
         WHERE type='search'
           AND id NOT IN (select * FROM views)
    """
    )
    size = cr.rowcount
    abacus = count()
    for (vid,) in util.log_progress(cr.fetchall(), util._logger, qualifier="search views", size=size):
        with util.edit_view(cr, view_id=vid) as view:
            for node in view.xpath("//filter[not(@name)][not(@position)]"):
                node.attrib["name"] = "s%d" % next(abacus)
