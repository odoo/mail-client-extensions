/**
 * Format the given URL by checking the protocol part and removing trailing "/".
 */
export function formatUrl(url: string): string {
    if (!url || !url.length) {
        return;
    }
    if (url.indexOf("http://") !== 0 && url.indexOf("https://") !== 0) {
        url = "https://" + url;
    }

    // Remove trailing "/"
    return url.replace(/\/+$/, "");
}

/**
 * Truncate the given text to not exceed the given length.
 */
export function truncate(str: string, maxLength: number) {
    if (str.length > maxLength) {
        return str.substring(0, maxLength - 3) + "...";
    }
    return str;
}
