/**
 * Object which fetchs the translations on the Odoo database, puts them in cache.
 *
 * Done in a class and not in a simple function so we read only once the cache for all
 * translations.
 */
var Translate = /** @class */ (function () {
    function Translate() {
        var cache = CacheService.getUserCache();
        var cacheKey = "ODOO_TRANSLATIONS";
        var translationsStr = cache.get(cacheKey);
        if (translationsStr) {
            this.translations = JSON.parse(translationsStr);
        } else if (State.odooServerUrl && State.accessToken) {
            Logger.log("Download translations...");
            this.translations = (0, postJsonRpc)(
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
    Translate.prototype._t = function (text, parameters) {
        if (parameters === void 0) {
            parameters = undefined;
        }
        var translated = this.translations[text];
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
            var re = new RegExp(
                Object.keys(parameters)
                    .map(function (x) {
                        return "%\\(".concat(x, "\\)s");
                    })
                    .join("|"),
                "gi",
            );
            return translated.replace(re, function (key) {
                return parameters[key.substring(2, key.length - 2)] || "";
            });
        }
    };
    return Translate;
})();
var translate = new Translate();
// Can be used as a function without reading each time the cache
function _t(text, parameters) {
    if (parameters === void 0) {
        parameters = undefined;
    }
    return translate._t(text, parameters);
}
function clearTranslationCache() {
    var cache = CacheService.getUserCache();
    var cacheKey = "ODOO_TRANSLATIONS";
    cache.remove(cacheKey);
    translate.translations = {};
}
