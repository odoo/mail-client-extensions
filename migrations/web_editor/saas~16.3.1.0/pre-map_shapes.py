import re

import odoo.upgrade.util.snippets as snip

web_editor_shape_mapping = {
    "line/little_lines_1": "composition/composition_line_1",
    "line/little_lines_2": "composition/composition_line_2",
    "line/little_lines_3": "composition/composition_line_3",
    "float/flt_primary_1": "composition/composition_mixed_1",
    "float/flt_primary_2": "composition/composition_mixed_2",
    "line/organic_1_line": "composition/composition_organic_line",
    "line/oval_2_line": "composition/composition_oval_line",
    "float/flt_planets_1": "composition/composition_planet_1",
    "float/flt_planets_2": "composition/composition_planet_2",
    "float/flt_square_1": "composition/composition_square_1",
    "float/flt_square_2": "composition/composition_square_2",
    "float/flt_square_3": "composition/composition_square_3",
    "float/flt_square_4": "composition/composition_square_4",
    "line/line_square_1": "composition/composition_square_line",
    "line/line_triangle": "composition/composition_triangle_line",
    "basic/bsc_square_1": "geometric/geo_square_1",
    "basic/bsc_square_2": "geometric/geo_square_2",
    "basic/bsc_square_3": "geometric/geo_square_3",
    "basic/bsc_square_4": "geometric/geo_square_4",
    "basic/bsc_square_5": "geometric/geo_square_5",
    "basic/bsc_square_6": "geometric/geo_square_6",
    "basic/bsc_organic_3": "geometric_round/geo_round_blob_hard",
    "basic/bsc_organic_2": "geometric_round/geo_round_blob_medium",
    "basic/bsc_organic_1": "geometric_round/geo_round_blob_soft",
    "basic/bsc_square_rounded_1": "geometric_round/geo_round_square_1",
    "basic/bsc_square_rounded_2": "geometric_round/geo_round_square_2",
    "special/spl_circuit_1": "pattern/pattern_circuit",
    "line/line_star": "pattern/pattern_line_star",
    "line/line_sun": "pattern/pattern_line_sun",
    "pattern/organic_4_pattern_caps": "pattern/pattern_organic_caps",
    "pattern/organic_3_pattern_cross": "pattern/pattern_organic_cross",
    "pattern/organic_2_pattern_dot": "pattern/pattern_organic_dot",
    "line/oval_3_pattern_line": "pattern/pattern_oval_zebra",
    "pattern/pattern_points_1": "pattern/pattern_point",
    "pattern/pattern_waves_1": "pattern/pattern_wave_1",
    "pattern/pattern_waves_2": "pattern/pattern_wave_2",
    "pattern/pattern_waves_4": "pattern/pattern_wave_3",
    "pattern/pattern_waves_3": "pattern/pattern_wave_4",
    "solid/blob_1_solid_rd": "solid/solid_blob_1",
    "solid/blob_2_solid_str": "solid/solid_blob_2",
    "solid/blob_3_solid_rd": "solid/solid_blob_3",
    "solid/oval_1_solid_rd": "solid/solid_blob_4",
    "solid/sld_blob_4": "solid/solid_blob_5",
    "solid/sld_blob_shadow_1": "solid/solid_blob_shadow_1",
    "solid/sld_blob_shadow_2": "solid/solid_blob_shadow_2",
    "solid/sld_square_1": "solid/solid_square_1",
    "solid/sld_square_2": "solid/solid_square_2",
    "solid/sld_square_organic_1": "solid/solid_square_3",
    "special/spl_filter_1": "special/special_filter",
    "special/spl_flag_1": "special/special_flag",
    "float/flt_primary_3": "special/special_layered",
    "special/spl_organics_1": "special/special_organic",
    "special/spl_rain_1": "special/special_rain",
    "special/spl_snow_1": "special/special_snow",
    "special/spl_speed_1": "special/special_speed",
}

mass_mailing_shape_mapping = {
    "basic/circle": "geometric_round/geo_round_circle",
    "basic/triangle": "geometric/geo_cornered_triangle",
    "basic/slanted": "geometric/geo_slanted",
}

patterns = [
    (
        "src",
        re.compile(r"/web_editor/image_shape/(?P<image>.+)/(?P<module>web_editor|mass_mailing)/(?P<shape>.+)\.svg"),
        "/web_editor/image_shape/%(image)s/web_editor/%(shape)s.svg",
    ),
    (
        "data-shape",
        re.compile(r"(?P<module>web_editor|mass_mailing)/(?P<shape>.+)"),
        "web_editor/%(shape)s",
    ),
]


def convert_shape(el):
    changed = False
    for attr, regex, pattern in patterns:
        value = el.get(attr)
        if not value:
            continue
        match = regex.match(value)
        if match:
            target_shape = None
            groups = match.groupdict()
            if groups["module"] == "mass_mailing":
                target_shape = mass_mailing_shape_mapping.get(groups["shape"])
            else:  # web_editor
                target_shape = web_editor_shape_mapping.get(groups["shape"])
            if target_shape:
                groups["shape"] = target_shape
                el.set(attr, pattern % groups)
                changed = True
    return changed


def migrate(cr, version):
    snip.convert_html_content(
        cr,
        snip.html_converter(convert_shape, selector="//img[@data-shape]"),
        where_column=r"~ '\ydata-shape=\"'",
    )
