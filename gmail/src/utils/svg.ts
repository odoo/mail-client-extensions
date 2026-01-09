import { Resvg } from "@resvg/resvg-js";
import { Response } from "express";
import path from "path";

/**
 * On the 19 December 2025, Google doesn't cache SVG files
 * (it doesn't even fetch the route if it ends with `.svg`)
 * Because we need to translate the text in some images,
 * we dynamically convert the SVG to PNG.
 *
 * In practice, this route is called once, and then Google caches the PNG.
 */
export function svgToPngResponse(svgContent: NonSharedBuffer, res: Response) {
    const fontFiles = [
        path.join(__dirname, "../assets", "GoogleSans.ttf"),
        // Manuscript font used by some images
        path.join(__dirname, "../assets", "Caveat.ttf"),
    ];

    const resvg = new Resvg(svgContent, {
        fitTo: { mode: "width", value: 320 },
        font: {
            fontFiles: fontFiles,
            loadSystemFonts: false,
            // Font used by Gmail
            defaultFontFamily: "Google Sans",
        },
    });

    res.set("Content-Type", "image/png");
    res.set("Cache-Control", "public, immutable, max-age=31536000");
    res.send(resvg.render().asPng());
}
