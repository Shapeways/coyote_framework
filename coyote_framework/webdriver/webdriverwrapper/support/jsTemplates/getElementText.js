/* Usage: replace all variables prefaced with '%' then execute file text as a string */


try {
    /* Returns the inner text of element */
    var text = $(arguments[0]).text();

    return text;

} catch (ex) {
    /* pass the error to the js executor function */
    return ex;
}
