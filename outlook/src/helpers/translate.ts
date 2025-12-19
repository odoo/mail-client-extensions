import API from './api'
import { postJsonRpc } from './http'

//Threshold in miliseconds after which translations are considered as expired
const EXPIRATION_TRESHOLD = 24 * 60 * 60 * 1000 //set to 24 hours

function getTranslations(): Record<string, string> | null {
    try {
        return JSON.parse(localStorage.getItem('translations'))
    } catch (e) {
        return null
    }
}

export async function fetchTranslations() {
    if (!translationsExpired()) {
        return
    }
    const result = await postJsonRpc(API.GET_TRANSLATIONS, {
        plugin: 'outlook',
    })
    if (result) {
        saveTranslations(result)
    }
}

/**
 * Returns true if there are no translations or if translations have expired)
 */
function translationsExpired(): boolean {
    if (getTranslations() == null) {
        return true
    }
    const translationsDate = new Date(
        Number(localStorage.getItem('translationsTimestamp'))
    )
    return Date.now() - translationsDate.getTime() >= EXPIRATION_TRESHOLD
}

/**
 * saves translations in local storage
 * @param translations translations to save
 */
function saveTranslations(translations: string[]): void {
    localStorage.setItem('translations', JSON.stringify(translations))
    localStorage.setItem('translationsTimestamp', JSON.stringify(Date.now()))
}

/**
 * returns a string's corresponding translation, if no translation is found, fallsback to the input string itself
 * @param s the string to translate
 * @param params corresponding value for each "%(param)s" found in the string.
 */
export function _t(text: string, parameters?: any): string {
    const translations = getTranslations() as Record<string, string>
    let translated = translations ? translations[text] : text

    if (!translated) {
        translated = text
    }

    if (parameters === undefined) {
        return translated
    } else if (
        typeof parameters === 'string' ||
        typeof parameters === 'number'
    ) {
        // "%s" % variable
        return translated.replace(/%s/i, '' + parameters)
    } else {
        // "%(variable_1)s at %(variable_2)s" % {variable_1: value, variable_2: value}
        const re = new RegExp(
            Object.keys(parameters)
                .map((x) => `%\\(${x}\\)s`)
                .join('|'),
            'gi'
        )
        return translated.replace(
            re,
            (key: string) => parameters[key.substring(2, key.length - 2)] || ''
        )
    }
}
