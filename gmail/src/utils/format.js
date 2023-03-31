/**
 * Format the given URL by checking the protocol part and removing trailing "/".
 */
function formatUrl(url) {
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
function isTrue(value) {
    if (value && value.length) {
        return value;
    }
}
/**
 * Return the first element of an array if the array is not null and not empty.
 */
function first(value) {
    if (value && value.length) {
        return value[0];
    }
}
/**
 * Repeat the given string "n" times.
 */
function repeat(str, n) {
    var result = "";
    while (n > 0) {
        result += str;
        n--;
    }
    return result;
}
/**
 * Truncate the given text to not exceed the given length.
 */
function truncate(str, maxLength) {
    if (str.length > maxLength) {
        return str.substring(0, maxLength - 3) + "...";
    }
    return str;
}
