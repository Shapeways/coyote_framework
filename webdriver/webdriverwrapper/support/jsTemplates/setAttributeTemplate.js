/* Usage: replace all variables prefaced with '%' then execute file text as a string */

/* %selector: a CSS selector to query the element */
/* %attribute_name: the name of the attribute to set */
/* %attribute_value: the value to set the attribute to */

try {
    var element = arguments[0]; /* must pass the WebElement instance in execute_script (NOT WebElementWrapper) */
    element.setAttribute('%attribute_name', '%attribute_value');

    /* so that true will be passed to js executor function */
    return true;

} catch (ex) {
    /* pass the error to the js executor function */
    return ex;
}
