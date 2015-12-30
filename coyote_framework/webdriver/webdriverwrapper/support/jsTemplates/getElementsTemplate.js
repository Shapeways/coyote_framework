/* Usage: replace all variables prefaced with '%' then execute file text as a string */

/* %selector: the selector to find the element(s) */

try {
    /* Returns the inner text of all elements matching the selector, stripping out all whitespace */
    var elements = document.querySelectorAll('%selector');

    return elements;

} catch (ex) {
    /* pass the error to the js executor function */
    return ex;
}
