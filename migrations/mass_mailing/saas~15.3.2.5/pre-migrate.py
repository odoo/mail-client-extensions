# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mass_mailing.mailing_list_view_form_simplified_footer")
    util.remove_record(cr, "mass_mailing.open_create_mass_mailing_list")

    util.create_column(cr, "mailing_mailing", "favorite", "boolean")
    util.create_column(cr, "mailing_mailing", "favorite_date", "timestamp without time zone")
