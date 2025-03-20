from odoo.upgrade import util


def migrate(cr, version):
    # the mapping is not direct for some fields.
    # when a report line has several columns, these correspond to different report fields
    # but there is no code on expressions, so we have to match using both line code and the expression label
    fields_mapping = {
        "book_records_documents": {"code": "L10N_LU_TAX_238", "label": "balance"},
        "phone_number": {"code": "L10N_LU_TAX_237", "label": "balance"},
        "avg_nb_employees_with_salary": {"code": "L10N_LU_TAX_108", "label": "balance"},
        "avg_nb_employees_with_no_salary": {"code": "L10N_LU_TAX_109", "label": "balance"},
        "submitted_rcs": {"code": "L10N_LU_TAX_998", "label": "balance"},
        "report_section_192": {"code": "L10N_LU_TAX_192", "label": "vat_excluded"},
        "report_section_193": {"code": "L10N_LU_TAX_192", "label": "vat_invoiced"},
        "report_section_239": {"code": "L10N_LU_TAX_239", "label": "total"},
        "report_section_240": {"code": "L10N_LU_TAX_239", "label": "percent"},
        "report_section_114": {"code": "L10N_LU_TAX_239", "label": "vat_excluded"},
        "report_section_241": {"code": "L10N_LU_TAX_241", "label": "total"},
        "report_section_242": {"code": "L10N_LU_TAX_241", "label": "percent"},
        "report_section_243": {"code": "L10N_LU_TAX_241", "label": "vat_excluded"},
        "report_section_244": {"code": "L10N_LU_TAX_244", "label": "total"},
        "report_section_245": {"code": "L10N_LU_TAX_244", "label": "percent"},
        "report_section_246": {"code": "L10N_LU_TAX_244", "label": "vat_excluded"},
        "report_section_247": {"code": "L10N_LU_TAX_247", "label": "total"},
        "report_section_248": {"code": "L10N_LU_TAX_247", "label": "percent"},
        "report_section_249": {"code": "L10N_LU_TAX_247", "label": "vat_excluded"},
        "report_section_250": {"code": "L10N_LU_TAX_250", "label": "total"},
        "report_section_251": {"code": "L10N_LU_TAX_250", "label": "percent"},
        "report_section_252": {"code": "L10N_LU_TAX_250", "label": "vat_excluded"},
        "report_section_253": {"code": "L10N_LU_TAX_253", "label": "total"},
        "report_section_254": {"code": "L10N_LU_TAX_253", "label": "percent"},
        "report_section_255": {"code": "L10N_LU_TAX_253", "label": "vat_excluded"},
        "report_section_256": {"code": "L10N_LU_TAX_256", "label": "total"},
        "report_section_257": {"code": "L10N_LU_TAX_256", "label": "percent"},
        "report_section_258": {"code": "L10N_LU_TAX_256", "label": "vat_excluded"},
        "report_section_259": {"code": "L10N_LU_TAX_256", "label": "vat_invoiced"},
        "report_section_260": {"code": "L10N_LU_TAX_260", "label": "total"},
        "report_section_261": {"code": "L10N_LU_TAX_260", "label": "percent"},
        "report_section_262": {"code": "L10N_LU_TAX_260", "label": "vat_excluded"},
        "report_section_263": {"code": "L10N_LU_TAX_260", "label": "vat_invoiced"},
        "report_section_265": {"code": "L10N_LU_TAX_265", "label": "total"},
        "report_section_266": {"code": "L10N_LU_TAX_265", "label": "percent"},
        "report_section_267": {"code": "L10N_LU_TAX_265", "label": "vat_excluded"},
        "report_section_268": {"code": "L10N_LU_TAX_265", "label": "vat_invoiced"},
        "report_section_269": {"code": "L10N_LU_TAX_269", "label": "total"},
        "report_section_270": {"code": "L10N_LU_TAX_269", "label": "percent"},
        "report_section_271": {"code": "L10N_LU_TAX_269", "label": "vat_excluded"},
        "report_section_272": {"code": "L10N_LU_TAX_269", "label": "vat_invoiced"},
        "report_section_274": {"code": "L10N_LU_TAX_274", "label": "total"},
        "report_section_275": {"code": "L10N_LU_TAX_274", "label": "percent"},
        "report_section_276": {"code": "L10N_LU_TAX_274", "label": "vat_excluded"},
        "report_section_277": {"code": "L10N_LU_TAX_274", "label": "vat_invoiced"},
        "report_section_279": {"code": "L10N_LU_TAX_279", "label": "total"},
        "report_section_280": {"code": "L10N_LU_TAX_279", "label": "percent"},
        "report_section_281": {"code": "L10N_LU_TAX_279", "label": "vat_excluded"},
        "report_section_282": {"code": "L10N_LU_TAX_279", "label": "vat_invoiced"},
        "report_section_283": {"code": "L10N_LU_TAX_283", "label": "total"},
        "report_section_284": {"code": "L10N_LU_TAX_283", "label": "percent"},
        "report_section_183": {"code": "L10N_LU_TAX_283", "label": "vat_excluded"},
        "report_section_184": {"code": "L10N_LU_TAX_283", "label": "vat_invoiced"},
        "report_section_285": {"code": "L10N_LU_TAX_285", "label": "total"},
        "report_section_286": {"code": "L10N_LU_TAX_285", "label": "percent"},
        "report_section_287": {"code": "L10N_LU_TAX_285", "label": "vat_excluded"},
        "report_section_288": {"code": "L10N_LU_TAX_285", "label": "vat_invoiced"},
        "report_section_289": {"code": "L10N_LU_TAX_289", "label": "total"},
        "report_section_290": {"code": "L10N_LU_TAX_289", "label": "percent"},
        "report_section_291": {"code": "L10N_LU_TAX_289", "label": "vat_excluded"},
        "report_section_292": {"code": "L10N_LU_TAX_289", "label": "vat_invoiced"},
        "report_section_293": {"code": "L10N_LU_TAX_293", "label": "total"},
        "report_section_294": {"code": "L10N_LU_TAX_293", "label": "percent"},
        "report_section_295": {"code": "L10N_LU_TAX_293", "label": "vat_excluded"},
        "report_section_296": {"code": "L10N_LU_TAX_293", "label": "vat_invoiced"},
        "report_section_297": {"code": "L10N_LU_TAX_297", "label": "total"},
        "report_section_298": {"code": "L10N_LU_TAX_297", "label": "percent"},
        "report_section_299": {"code": "L10N_LU_TAX_297", "label": "vat_excluded"},
        "report_section_300": {"code": "L10N_LU_TAX_297", "label": "vat_invoiced"},
        "report_section_301": {"code": "L10N_LU_TAX_301", "label": "total"},
        "report_section_302": {"code": "L10N_LU_TAX_301", "label": "percent"},
        "report_section_303": {"code": "L10N_LU_TAX_301", "label": "vat_excluded"},
        "report_section_304": {"code": "L10N_LU_TAX_301", "label": "vat_invoiced"},
        "report_section_305": {"code": "L10N_LU_TAX_305", "label": "total"},
        "report_section_306": {"code": "L10N_LU_TAX_305", "label": "percent"},
        "report_section_185": {"code": "L10N_LU_TAX_305", "label": "vat_excluded"},
        "report_section_186": {"code": "L10N_LU_TAX_305", "label": "vat_invoiced"},
        "report_section_307": {"code": "L10N_LU_TAX_307", "label": "total"},
        "report_section_308": {"code": "L10N_LU_TAX_307", "label": "percent"},
        "report_section_309": {"code": "L10N_LU_TAX_307", "label": "vat_excluded"},
        "report_section_310": {"code": "L10N_LU_TAX_310", "label": "total"},
        "report_section_311": {"code": "L10N_LU_TAX_310", "label": "percent"},
        "report_section_312": {"code": "L10N_LU_TAX_310", "label": "vat_excluded"},
        "report_section_313": {"code": "L10N_LU_TAX_310", "label": "vat_invoiced"},
        "report_section_314": {"code": "L10N_LU_TAX_314", "label": "percent"},
        "report_section_315": {"code": "L10N_LU_TAX_314", "label": "vat_excluded"},
        "report_section_316": {"code": "L10N_LU_TAX_316", "label": "percent"},
        "report_section_317": {"code": "L10N_LU_TAX_316", "label": "vat_excluded"},
        "report_section_319": {"code": "L10N_LU_TAX_319", "label": "vat_excluded"},
        "report_section_320": {"code": "L10N_LU_TAX_319", "label": "vat_invoiced"},
        "report_section_322": {"code": "L10N_LU_TAX_322", "label": "vat_excluded"},
        "report_section_323": {"code": "L10N_LU_TAX_322", "label": "vat_invoiced"},
        "report_section_328": {"code": "L10N_LU_TAX_328", "label": "vat_excluded"},
        "report_section_329": {"code": "L10N_LU_TAX_328", "label": "vat_invoiced"},
        "report_section_332": {"code": "L10N_LU_TAX_332", "label": "vat_excluded"},
        "report_section_333": {"code": "L10N_LU_TAX_332", "label": "vat_invoiced"},
        "report_section_334": {"code": "L10N_LU_TAX_334", "label": "vat_excluded"},
        "report_section_335": {"code": "L10N_LU_TAX_334", "label": "vat_invoiced"},
        "report_section_337": {"code": "L10N_LU_TAX_337", "label": "vat_excluded"},
        "report_section_338": {"code": "L10N_LU_TAX_337", "label": "vat_invoiced"},
        "report_section_115": {"code": "L10N_LU_TAX_115", "label": "vat_excluded"},
        "report_section_187": {"code": "L10N_LU_TAX_115", "label": "vat_invoiced"},
        "report_section_188": {"code": "L10N_LU_TAX_188", "label": "vat_excluded"},
        "report_section_189": {"code": "L10N_LU_TAX_188", "label": "vat_invoiced"},
        "report_section_343": {"code": "L10N_LU_TAX_343", "label": "vat_excluded"},
        "report_section_344": {"code": "L10N_LU_TAX_343", "label": "vat_invoiced"},
        "report_section_345": {"code": "L10N_LU_TAX_345", "label": "vat_excluded"},
        "report_section_346": {"code": "L10N_LU_TAX_345", "label": "vat_invoiced"},
        "report_section_347": {"code": "L10N_LU_TAX_347", "label": "vat_excluded"},
        "report_section_348": {"code": "L10N_LU_TAX_347", "label": "vat_invoiced"},
        "report_section_349": {"code": "L10N_LU_TAX_349", "label": "vat_excluded"},
        "report_section_350": {"code": "L10N_LU_TAX_349", "label": "vat_invoiced"},
        "report_section_351": {"code": "L10N_LU_TAX_351", "label": "vat_excluded"},
        "report_section_352": {"code": "L10N_LU_TAX_351", "label": "vat_invoiced"},
        "report_section_353": {"code": "L10N_LU_TAX_353", "label": "vat_excluded"},
        "report_section_354": {"code": "L10N_LU_TAX_353", "label": "vat_invoiced"},
        "report_section_355": {"code": "L10N_LU_TAX_355", "label": "vat_excluded"},
        "report_section_356": {"code": "L10N_LU_TAX_355", "label": "vat_invoiced"},
        "report_section_358": {"code": "L10N_LU_TAX_358", "label": "vat_excluded"},
        "report_section_359": {"code": "L10N_LU_TAX_358", "label": "vat_invoiced"},
        "report_section_361": {"code": "L10N_LU_TAX_361", "label": "vat_excluded"},
        "report_section_362": {"code": "L10N_LU_TAX_361", "label": "vat_invoiced"},
        "report_section_190": {"code": "L10N_LU_TAX_190", "label": "vat_excluded"},
        "report_section_191": {"code": "L10N_LU_TAX_190", "label": "vat_invoiced"},
        "report_section_168": {"code": "L10N_LU_TAX_168", "label": "year_start"},
        "report_section_181": {"code": "L10N_LU_TAX_168", "label": "year_end"},
        "report_section_163": {"code": "L10N_LU_TAX_163", "label": "year_start"},
        "report_section_176": {"code": "L10N_LU_TAX_163", "label": "year_end"},
        "report_section_791": {"code": "L10N_LU_TAX_791", "label": "year_start"},
        "report_section_792": {"code": "L10N_LU_TAX_791", "label": "year_end"},
        "report_section_991": {"code": "L10N_LU_TAX_991", "label": "year_start"},
        "report_section_992": {"code": "L10N_LU_TAX_991", "label": "year_end"},
        "report_section_793": {"code": "L10N_LU_TAX_793", "label": "year_start"},
        "report_section_794": {"code": "L10N_LU_TAX_793", "label": "year_end"},
        "report_section_993": {"code": "L10N_LU_TAX_993", "label": "year_start"},
        "report_section_994": {"code": "L10N_LU_TAX_993", "label": "year_end"},
        "report_section_797": {"code": "L10N_LU_TAX_797", "label": "year_start"},
        "report_section_798": {"code": "L10N_LU_TAX_797", "label": "year_end"},
        "report_section_795": {"code": "L10N_LU_TAX_795", "label": "year_start"},
        "report_section_796": {"code": "L10N_LU_TAX_795", "label": "year_end"},
        "report_section_995": {"code": "L10N_LU_TAX_995", "label": "year_start"},
        "report_section_996": {"code": "L10N_LU_TAX_995", "label": "year_end"},
        "report_section_158": {"code": "L10N_LU_TAX_158", "label": "year_start"},
        "report_section_171": {"code": "L10N_LU_TAX_158", "label": "year_end"},
        "report_section_162": {"code": "L10N_LU_TAX_162", "label": "year_start"},
        "report_section_175": {"code": "L10N_LU_TAX_162", "label": "year_end"},
        "report_section_200": {"code": "L10N_LU_TAX_200", "label": "year_start"},
        "report_section_201": {"code": "L10N_LU_TAX_200", "label": "year_end"},
        "report_section_164": {"code": "L10N_LU_TAX_164", "label": "year_start"},
        "report_section_177": {"code": "L10N_LU_TAX_164", "label": "year_end"},
        "report_section_165": {"code": "L10N_LU_TAX_165", "label": "year_start"},
        "report_section_178": {"code": "L10N_LU_TAX_165", "label": "year_end"},
        "report_section_167": {"code": "L10N_LU_TAX_167", "label": "year_start"},
        "report_section_180": {"code": "L10N_LU_TAX_167", "label": "year_end"},
        "report_section_116": {"code": "L10N_LU_TAX_116", "label": "year_start"},
        "report_section_117": {"code": "L10N_LU_TAX_116", "label": "year_end"},
        "report_section_118": {"code": "L10N_LU_TAX_118", "label": "year_start"},
        "report_section_119": {"code": "L10N_LU_TAX_118", "label": "year_end"},
        "report_section_120": {"code": "L10N_LU_TAX_120", "label": "year_start"},
        "report_section_121": {"code": "L10N_LU_TAX_120", "label": "year_end"},
    }

    util.create_column(cr, "l10n_lu_reports_report_appendix_expenditures", "year", "varchar")
    util.create_column(cr, "l10n_lu_reports_report_appendix_expenditures", "company_id", "int4")

    # this table has many many columns, so it's easier to fetch them along with their data type
    cr.execute(
        r"""
            SELECT c.COLUMN_NAME, c.data_type
              FROM information_schema.columns c
             WHERE table_name='l10n_lu_yearly_tax_report_manual'
               AND (
                       c.COLUMN_NAME LIKE 'report\_section\_%%'
                    -- extra fields that don't match the regular report_section_% pattern
                    OR c.COLUMN_NAME IN (
                        'book_records_documents',
                        'phone_number',
                        'avg_nb_employees_with_salary',
                        'avg_nb_employees_with_no_salary',
                        'submitted_rcs'
                        )
                   )
        """
    )

    fields = cr.fetchall()

    cr.execute(
        """
            SELECT ARRAY_AGG(tax_unit_company.res_company_id ORDER BY tax_unit_company.res_company_id),
                   main_company_id
              FROM account_tax_unit tax_unit
              JOIN account_tax_unit_res_company_rel tax_unit_company
                ON tax_unit_company.account_tax_unit_id = tax_unit.id
             WHERE tax_unit.country_id=%s
          GROUP BY main_company_id
        """,
        (util.ref(cr, "base.lu"),),
    )
    # reverse map from tax unit companies into their main company
    tax_unit_companies = {tuple(sorted(set(r[0]))): r[1] for r in cr.fetchall()}

    cr.execute(
        """
            SELECT c.l10n_lu_yearly_tax_report_manual_id,
                   ARRAY_AGG(c.res_company_id ORDER BY c.res_company_id)
              FROM l10n_lu_yearly_tax_report_manual_res_company_rel c
          GROUP BY c.l10n_lu_yearly_tax_report_manual_id
        """
    )
    main_company_per_report = {}
    for manual_report_id, manual_report_company_ids in cr.fetchall():
        # if all companies match those in the tax unit, take the unit main company
        # otherwise we take the first company by id
        main_company_per_report[manual_report_id] = tax_unit_companies.get(
            tuple(sorted(set(manual_report_company_ids))), manual_report_company_ids[0]
        )

    queries = []
    # fetch all the manual reports
    cr.execute("SELECT id, year FROM l10n_lu_yearly_tax_report_manual")
    for report_id, year in cr.fetchall():
        # if the company is in a tax unit, change the company_id to the main company of that tax unit
        # if the tax unit companies match the report companies
        report_company_id = main_company_per_report[report_id]

        params_dict = {
            "year": year,
            "company_id": report_company_id,
            "report_id": report_id,
        }

        for field, data_type in fields:
            label = fields_mapping[field]["label"] if field in fields_mapping else "balance"
            line_code = (
                fields_mapping[field]["code"] if field in fields_mapping else f"L10N_LU_TAX_{field.split('_')[-1]}"
            )
            column = "value" if data_type in {"integer", "boolean", "double precision"} else "text_value"
            if data_type == "boolean":
                # boolean fields became float fields in account.report, where 1.00 is True
                field_expression = util.format_query(cr, "{}::int::double precision", field)
            else:
                field_expression = field

            query = util.format_query(
                cr,
                """
                    WITH expr AS (
                        SELECT e.id
                          FROM account_report_expression e
                          JOIN account_report_line l
                            ON l.id=e.report_line_id
                         WHERE e.engine='external'
                           AND e.label=%(label)s
                           AND l.code=%(line_code)s
                    )
                    INSERT INTO account_report_external_value(name, {column}, date, target_report_expression_id, company_id)
                         SELECT 'Manual value', report.{field_expression},  CONCAT(%(year)s, '-12-31')::DATE, expr.id, %(company_id)s
                           FROM expr,
                                l10n_lu_yearly_tax_report_manual report
                          WHERE report.id=%(report_id)s
                """,
                column=column,
                field_expression=field_expression,
            )
            queries.append(
                cr.mogrify(
                    query,
                    {
                        **params_dict,
                        "label": label,
                        "line_code": line_code,
                    },
                ).decode()
            )

        # move the year and company_id fields from the manual report to expenditures
        queries.append(
            cr.mogrify(
                """
                    UPDATE l10n_lu_reports_report_appendix_expenditures a
                       SET year=m.year,
                           company_id=%s
                      FROM l10n_lu_yearly_tax_report_manual m
                     WHERE m.id=%s
                """,
                (report_company_id, report_id),
            )
        )

    util.parallel_execute(cr, queries)

    for view in (
        "view_l10n_lu_yearly_tax_report_manual",
        "l10n_lu_yearly_tax_report_manual_view_tree",
        "l10n_lu_yearly_tax_report_manual_view_kanban",
    ):
        util.remove_view(cr, f"l10n_lu_reports.{view}")

    util.remove_menus(cr, [util.ref(cr, "l10n_lu_reports.menu_action_l10n_lu_yearly_tax_report_manual")])
    for record in (
        "action_l10n_lu_yearly_tax_report_manual",
        "multi_company_annual_tax_report_view_rule",
    ):
        util.remove_record(cr, f"l10n_lu_reports.{record}")

    util.remove_field(cr, "l10n_lu_reports.report.appendix.expenditures", "report_id")
    util.remove_model(cr, "l10n_lu.yearly.tax.report.manual")
