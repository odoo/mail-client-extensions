import base64
from pathlib import Path

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "base.MVR", util.update_record_from_xml)
    cr.execute(
        """
        SELECT id
          FROM res_company
         WHERE layout_background = 'Geometric'
        """
    )
    if cr.rowcount:
        cids = [cid for (cid,) in cr.fetchall()]
        env = util.env(cr)
        background_image = (Path(__file__).parent / "bg_background_template.jpg").read_bytes()
        env["res.company"].browse(cids).write({"layout_background_image": base64.encodebytes(background_image)})

    util.change_field_selection_values(cr, "res.company", "layout_background", {"Geometric": "Custom"})
