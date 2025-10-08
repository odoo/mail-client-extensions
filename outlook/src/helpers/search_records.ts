import { ErrorMessage } from '../models/error_message'
import API from './api'
import { postJsonRpc } from './http'

/**
 * Search records of the given model.
 */
export async function searchRecords(
    recordModel: string,
    query: string
): Promise<[any[], number, ErrorMessage]> {
    const url = API.SEARCH_RECORDS + '/' + recordModel
    const response = await postJsonRpc(url, { query })

    if (!response?.length) {
        return [[], 0, new ErrorMessage('unknown', response.error)]
    }

    return [response[0], response[1], new ErrorMessage(null)]
}
