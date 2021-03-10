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
 * Return the given string only if it's not null and not empty.
 */
export function isTrue(value: any): string {
    if (value && value.length) {
        return value;
    }
}

/**
 * Return the first element of an array if the array is not null and not empty.
 */
export function first(value: any[]): any {
    if (value && value.length) {
        return value[0];
    }
}

/**
 * Repeat the given string "n" times.
 */
export function repeat(str: string, n: number) {
    let result = "";
    while (n > 0) {
        result += str;
        n--;
    }
    return result;
}
