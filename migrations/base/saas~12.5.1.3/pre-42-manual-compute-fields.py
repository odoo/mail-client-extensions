# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Prior to 13.0, the value of computed fields were initialized to `False` before computation.
    # From 13.0, this is no longer the case. Each record contained in `self` must have its field value assigned.
    # Therefore, if the compute method of a manual field is filled with blanks only,
    # the manual field raise an exception because after computation, the value for this field is still not in cache.
    # Updating the compute column to be completely empty makes it no longer seen as a compute field.
    cr.execute(
        r"""
            UPDATE ir_model_fields
               SET compute = ''
             WHERE state = 'manual'
              AND compute ~ '^[\s]+$'
        """
    )
