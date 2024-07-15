from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "rating_rating", "rated_on", "timestamp without time zone")
    util.remove_view(cr, "rating.rating_rating_view_form_complete")

    query = """
        UPDATE rating_rating rating
           SET rated_on = CASE WHEN res_model='project.task' THEN write_date
                               ELSE create_date
                          END
    """
    util.explode_execute(cr, query, table="rating_rating", alias="rating")
