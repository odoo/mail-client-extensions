from odoo.upgrade import util


def migrate(cr, version):
    query = """
        SELECT id
          FROM hr_leave
         WHERE duration_display IS NULL
    """
    util.recompute_fields(cr, "hr.leave", ["duration_display"], query=query)
