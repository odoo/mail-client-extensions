import { URLS } from "../consts";
import { User } from "../models/user";
import { postJsonRpc } from "../utils/http";

/**
 * Object which fetch the translations on the Odoo database, puts them in cache.
 *
 * Done in a class and not in a simple function so we read only once the cache for all
 * translations.
 */
export class Translate {
    translations: Record<string, string>;

    constructor(translations?: Record<string, string>) {
        this.translations = translations || {};
    }

    static async getTranslations(user: User): Promise<Function> {
        if (!user.translationsExpireAt || new Date() > user.translationsExpireAt) {
            user.translations = await postJsonRpc(
                user.odooUrl + URLS.GET_TRANSLATIONS,
                {},
                { Authorization: "Bearer " + user.odooToken },
            );
            // Store the translation for 6 hours
            const EXPIRATION_DURATION_MS = 6 * 60 * 60 * 1000;
            user.translationsExpireAt = new Date(Date.now() + EXPIRATION_DURATION_MS);
            await user.save();
            console.log("Translation fetched");
        }
        const translator = new Translate(user.translations);
        return translator._t.bind(translator);
    }

    /**
     * Translate the given string.
     *
     * This method supports python like string format. You can use named parameters
     * (e.g.: "Hello %(name)s") or simple string format (e.g.: "Hello %s").
     */
    _t(text: string, parameters: any = undefined): string {
        let translated = this.translations.hasOwnProperty(text) ? this.translations[text] : null;

        if (!translated) {
            if (this.translations && Object.keys(this.translations).length) {
                console.log("Translation missing for: " + text);
            }
            translated = text;
        }

        if (parameters === undefined) {
            return translated;
        } else if (typeof parameters === "string" || typeof parameters === "number") {
            // "%s" % variable
            return translated.replace(/%s/i, "" + parameters);
        } else {
            // "%(variable_1)s at %(variable_2)s" % {variable_1: value, variable_2: value}
            const re = new RegExp(
                Object.keys(parameters)
                    .map((x) => `%\\(${x}\\)s`)
                    .join("|"),
                "gi",
            );
            return translated.replace(
                re,
                (key) => parameters[key.substring(2, key.length - 2)] || "",
            );
        }
    }
}
