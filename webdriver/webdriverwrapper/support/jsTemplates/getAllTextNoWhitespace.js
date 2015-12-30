/* Usage: replace all variables prefaced with '%' then execute file text as a string */

/* %selector: the selector to find the element(s) */

try {
    /* Returns the inner text of all elements matching the selector, stripping out all whitespace */
    var text = $('%selector').text().replace(/\s+/g, '');

    return text;

} catch (ex) {
    /* pass the error to the js executor function */
    return ex;
}
