from odoo.upgrade import util

PERIOD_MAPPING = {
    "this_year": "year",
    "last_year": "year-1",
    "antepenultimate_year": "year-2",
    "this_month": "month",
    "last_month": "month-1",
    "antepenultimate_month": "month-2",
}


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id
          FROM ir_ui_view
         WHERE type = 'search'
           AND arch_db ->> 'en_US' LIKE '%default\_period%'
        """
    )
    for (view_id,) in cr.fetchall():
        with util.edit_view(cr, view_id=view_id, active=None) as arch:
            for node in arch.xpath("//filter[@date and @default_period]"):
                node.attrib["default_period"] = ",".join(
                    PERIOD_MAPPING.get(val, val) for val in node.attrib["default_period"].split(",")
                )
