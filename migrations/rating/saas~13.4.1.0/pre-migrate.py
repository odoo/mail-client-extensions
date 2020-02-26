# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE rating_rating SET rating = CEILING(rating / 2)")

    cr.execute(
        """
        UPDATE rating_rating
        SET rating_text = CASE
            WHEN rating >= 5 THEN 'satisfied'
            WHEN rating >= 3 THEN 'not_satisfied'
            WHEN rating >= 1 THEN 'highly_dissatisfied'
            ELSE 'no_rating' END"""
    )
