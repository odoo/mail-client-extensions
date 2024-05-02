import logging
import sys
import uuid
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat

from odoo.sql_db import db_connect

from odoo.upgrade import util

_logger = logging.getLogger(f"odoo.upgrade.base.saas-16.1.{__name__}")


def rm_last_update(dbname, model):
    cursor = db_connect(dbname).cursor
    with cursor() as cr:
        util.remove_field(cr, model, "__last_update", skip_inherit="*")
        cr.commit()


def migrate(cr, version):
    # There are so many models that we needs to remove the fields in parallel...
    _logger.info("Remove the `__last_update` field on *all* models.")

    cr.execute(
        """
        SELECT m.model
          FROM ir_model_fields f
          JOIN ir_model m
            ON m.id = f.model_id
         WHERE f.name = '__last_update'
        """
    )
    models = [row[0] for row in cr.fetchall()]

    wrong_models = [
        m
        for m in models
        # fmt: off
        if "_" in m
        if "." not in m
        if not m.startswith("x_")
        if m not in util.helpers._VALID_MODELS
        # fmt: on
    ]
    if wrong_models:
        _logger.warning("There appear to be some invalid model names %s", wrong_models)
        orig_valid_models = util.helpers._VALID_MODELS
        # avoid unnecesary failures in remove_field
        util.helpers._VALID_MODELS = frozenset(set(orig_valid_models) | set(wrong_models))

    cr.commit()  # Avoid deadlock as the processes will remove the `ir_model_fields` records

    # NOTE
    # `ProcessPoolExecutor.map` arguments needs to be pickleable
    # Functions can only be pickle if they are importable.
    # However, the current file is not importable due to the dash in the filename.
    # We should then put the executed function in its own importable file.
    name = f"_upgrade_{uuid.uuid4().hex}"
    mod = sys.modules[name] = util.import_script(__file__, name=name)

    # We cannot use Threads as `remove_field` call (directly and indirectly) `parallel_execute`,
    # which itself spawn threads, leading to the exhaustion of the ConnectionPool.
    with ProcessPoolExecutor(max_workers=util.get_max_workers()) as executor:
        list(
            util.log_progress(
                executor.map(mod.rm_last_update, repeat(cr.dbname), models),
                _logger,
                qualifier="models",
                size=len(models),
                estimate=False,
                log_hundred_percent=True,
            )
        )

    if wrong_models:
        util.helpers._VALID_MODELS = orig_valid_models
