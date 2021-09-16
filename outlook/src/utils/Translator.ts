//Threshold in miliseconds after which translations are considered as expired
const EXPIRATION_TRESHOLD = 24 * 60 * 60 * 1000; //set to 24 hours

function getTranslations(): String[] {
    try {
        return JSON.parse(localStorage.getItem('translations'));
    } catch (e) {
        return null;
    }
}

/**
 * Returns true if there are no translations or if translations have expired)
 */
export function translationsExpired(): boolean {
    if (getTranslations() == null) {
        return true;
    }
    const translationsDate = new Date(Number(localStorage.getItem('translationsTimestamp')));
    //check if translations have expired (are older then the threshold)
    return Date.now() - translationsDate.getTime() >= EXPIRATION_TRESHOLD;
}

/**
 * saves translations in local storage
 * @param translations translations to save
 */
export function saveTranslations(translations: String[]): void {
    localStorage.setItem('translations', JSON.stringify(translations));
    localStorage.setItem('translationsTimestamp', JSON.stringify(Date.now()));
}

/**
 * returns a string where each %(param)s is replaced by it's corresponding param
 * @param s input string which can contain some
 * @param params corresponding values for each "%(param)s" found in the string
 */

function subReplace(s: string, params?: any): string {
    if (params) {
        let replaced = s.replace(/%\((.+?)\)s/g, (g1, g2) => {
            if (params[g2] != undefined) {
                return params[g2];
            } else {
                return g1;
            }
        });
        return replaced;
    } else {
        return s;
    }
}

/**
 * returns a string's corresponding translation, if no translation is found, fallsback to the input string itself
 * @param s the string to translate
 * @param params corresponding value for each "%(param)s" found in the string.
 */
export function _t(s: string, params?: any): string {
    const translations = getTranslations() as string[];
    if (translations && translations[s]) {
        return subReplace(translations[s], params);
    } else {
        return subReplace(s, params);
    }
}
