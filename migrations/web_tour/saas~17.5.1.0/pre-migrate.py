from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("TRUNCATE web_tour_tour")
    util.remove_field(cr, "web_tour.tour", "user_id")
    util.create_column(cr, "res_users", "tour_enabled", "bool", default=False)
    util.remove_view(cr, "web_tour.edit_tour_search")
    util.remove_view(cr, "web_tour.edit_tour_list")
    util.remove_view(cr, "web_tour.edit_tour_form")
