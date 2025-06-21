from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "planning_slot_template", "name", "varchar")
    cr.execute(
        """
            UPDATE planning_slot_template
               SET name = concat(
                        to_char(to_timestamp((coalesce(start_time, 0)) * 60), 'MI:SS'),
                        ' - ',
                        to_char(to_timestamp((coalesce(end_time, 0)) * 60), 'MI:SS')
                   )
        """
    )
