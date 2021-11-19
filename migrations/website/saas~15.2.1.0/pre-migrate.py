# -*- coding: utf-8 -*-
import re

from lxml import etree, html

import odoo.upgrade.util.snippets as snip

utf8_parser = html.HTMLParser(encoding="utf-8")


def rgba_to_rbg(rgba):
    """
    Calculates RGB values in order to mix the RGBA given in parameters with
    white (taking 1-A as the white rate to add).

    :param rgba: list of 4 strings representing numbers (R, G, B, A)
    :return: list of 3 integers (R, G, B)
    """
    r = int(rgba[0]) / 255
    g = int(rgba[1]) / 255
    b = int(rgba[2]) / 255
    a = float(rgba[3])
    white_percentage = 1 - a
    new_r = int((white_percentage + r * (1 - white_percentage)) * 255)
    new_g = int((white_percentage + g * (1 - white_percentage)) * 255)
    new_b = int((white_percentage + b * (1 - white_percentage)) * 255)
    return [new_r, new_g, new_b]


def remove_transparency_effects(section_el):
    """
    Modifies the attributes of section_el so that it keeps the same rendering
    but without becoming transparent.

    :param section_el: lxml.html.HtmlElement
    """
    style_properties = snip.parse_style(section_el.get("style", ""))

    section_el.classes.add("o_colored_level")

    bg_image = style_properties.get("background-image")
    has_gradient = bg_image and "-gradient(" in bg_image
    if has_gradient:
        # In the case where there is a gradient, the colors that compose it can
        # have a transparency. If this is the case, the transparent colors must
        # be recalculated so that they look the same but without transparency.
        bg_image_post_gradient = bg_image.split("-gradient(", 1)[1]
        if "rgba" in bg_image_post_gradient:
            gradient_parts = bg_image_post_gradient.split("rgba")
            gradient_parts[0] = f"-gradient({gradient_parts[0]}"
            # Here, gradient_parts is a list of strings, the first element is the
            # string that precedes the first occurrence of "rgba". Others are
            # strings starting with "rgba" but which can contain more than one
            # color if the next color is not a rgba.
            for i in range(1, len(gradient_parts), 1):
                rgba_value = gradient_parts[i]
                # Eg: "(1, 2, 3, 0.5) *". * represents the string until the next
                # occurrence of "rgba".
                rgba = rgba_value.split("(")[1].split(")")[0].split(",")
                # The rgba value is a list of strings representing numbers
                # (R, G, B, A).
                rgb = rgba_to_rbg(rgba)
                gradient_parts[i] = f"{rgb[0]}, {rgb[1]}, {rgb[2]}){rgba_value.split(')', 1)[1]}"
                # gradient_parts[i] is for exemple: "2, 3, 4) *" * represents the
                # string until the next occurrence of "rgba".
            # Rebuild gradient_parts with the new RGB colors.
            gradient_parts = "rgb(".join(gradient_parts)
            # Rebuild background-image with the new gradient.
            style_properties["background-image"] = bg_image[:bg_image.index("-gradient(")] + gradient_parts

        # In case there is a gradient, we suppose it is a normal Odoo case with
        # a forced transparent color behind it. The gradient transparent color
        # were mixed with white and we have nothing else to change.
        section_el.set("style", snip.format_style(style_properties))
        return

    # In case there is bg-XXX class or bg-o-color-XXX class, we suppose the
    # background color is determined by it and we don't change anything else
    for class_name in section_el.classes:
        if (class_name.startswith("bg-") and class_name.count("-") == 1) or class_name.startswith("bg-o-color-"):
            return

    # Put an equivalent gray if there is a bg-black-* class.
    # Put a white background if there is a bg-white-* class.
    # We keep the class because in addition to affecting the background color,
    # it affects the text color and we don't want the text color to change.
    rgb_by_class = {
        "bg-black-15": "217",
        "bg-black-25": "191",
        "bg-black-50": "127",
        "bg-black-75": "64",
        "bg-white-85": "255",
        "bg-white-75": "255",
        "bg-white-50": "255",
        "bg-white-25": "255",
    }
    for class_name in rgb_by_class:
        if class_name in section_el.classes:
            rgb = rgb_by_class[class_name]
            style_properties["background-color"] = f"rgb({rgb}, {rgb}, {rgb}) !important"
            break

    # In case of custom color with transparency, the RGBA is recalculated to
    # keep an equivalent RGB color without transparency.
    if "background-color" in style_properties and "rgba" in style_properties["background-color"]:
        current_rgba = style_properties["background-color"].split("(")[1].split(")")[0].split(",")
        new_rgb = rgba_to_rbg(current_rgba)
        style_properties["background-color"] = f"rgb({new_rgb[0]}, {new_rgb[1]}, {new_rgb[2]}) !important"
    if "o_cc" not in section_el.classes and "background-color" not in style_properties:
        style_properties["background-color"] = "white !important"

    section_el.set("style", snip.format_style(style_properties))


def migrate(cr, version):
    """
    Ensure that the rendering of mega menu's background colors does not change
    with the arrival of transparency effects

    :param cr: database cursor
    :param version: version of the module
    """
    cr.execute(
        r"""
            SELECT w.id, w.mega_menu_content
            FROM website_menu w
            WHERE w.mega_menu_content IS NOT NULL
        """
    )
    for mega_menu_id, content in cr.fetchall():
        # Wrap in <wrap> node before parsing to preserve external comments and
        # multi-root nodes
        section_els = html.fromstring(f"<wrap>{content}</wrap>", parser=utf8_parser)
        for section_el in section_els:
            remove_transparency_effects(section_el)
        content = etree.tostring(section_els, encoding="unicode")
        content = re.sub(r"(^<wrap>|</wrap>$)", "", content.strip())
        cr.execute(
            r"""
                UPDATE website_menu
                SET mega_menu_content = %s
                WHERE website_menu.id = %s
            """,
            [content, mega_menu_id],
        )
