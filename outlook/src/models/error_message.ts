import { _t } from '../helpers/translate'

/**
 * Represent an error and translate its code to a message.
 */

const _ERROR_CODE_MESSAGES: Record<string, string> = {
    odoo: null, // Message is contained in the additional information
    http_error_odoo: 'Could not connect to database. Try to log out and in.',
    unknown: 'Something bad happened. Please, try again later.',
}

/**
 * Represent an error message which will be displayed on the add-on.
 * Translate the code into a message to display to the user.
 */
export class ErrorMessage {
    code: string
    message: string
    information: string

    constructor(code: string = null, information?: string) {
        if (code) {
            this.setError(code, information)
        }
    }

    /**
     * Set the code error and find the appropriate message to display.
     */
    setError(code: string, information?: string) {
        if (code === 'no_data') {
            code = 'missing_data'
            information = null
        }

        this.code = code
        this.information = information
        this.message = information || _t(_ERROR_CODE_MESSAGES[this.code])
    }
}
