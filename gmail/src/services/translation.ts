import { postJsonRpc } from "../utils/http";
import { State } from "../models/state";
import { URLS } from "../const";

/**
 * Object which fetchs the translations on the Odoo database, puts them in cache.
 *
 * Done in a class and not in a simple function so we read only once the cache for all
 * translations.
 */
export class Translate {
    translations: Record<string, string>;

    constructor() {
        const cache = CacheService.getUserCache();
        const cacheKey = "ODOO_TRANSLATIONS";

        const translationsStr = cache.get(cacheKey);

        if (translationsStr) {
            this.translations = JSON.parse(translationsStr);
        } else if (State.odooServerUrl && State.accessToken) {
            Logger.log("Download translations...");

            this.translations = postJsonRpc(
                State.odooServerUrl + URLS.GET_TRANSLATIONS,
                {},
                { Authorization: "Bearer " + State.accessToken },
            );

            if (this.translations) {
                // Put in the cacher for 6 hours (maximum cache life time)
                cache.put(cacheKey, JSON.stringify(this.translations), 21600);
            }
        }

        this.translations = this.translations || {};
    }

    /**
     * Translate the given string.
     *
     * This method supports python like string format. You can use named parameters
     * (e.g.: "Hello %(name)s") or simple string format (e.g.: "Hello %s").
     */
    _t(text: string, parameters: any = undefined): string {
        let translated = this.translations[text];

        if (!translated) {
            if (this.translations && Object.keys(this.translations).length) {
                Logger.log("Translation missing for: " + text);
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
            return translated.replace(re, (key) => parameters[key.substring(2, key.length - 2)] || "");
        }
    }
}

const translate = new Translate();

// Can be used as a function without reading each time the cache
export function _t(text: string, parameters: any = undefined): string {
    return translate._t(text, parameters);
}

export function clearTranslationCache() {
    const cache = CacheService.getUserCache();
    const cacheKey = "ODOO_TRANSLATIONS";
    cache.remove(cacheKey);
    translate.translations = {};
}
