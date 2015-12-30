/* Usage: replace all variables prefaced with '%' then execute file text as a string */

try {
    var element = arguments[0]; /* must pass the WebElement instance in execute_script (NOT WebElementWrapper) */
    element.click();

    /* so that true will be passed to js executor function */
    return true;

} catch (ex) {
    /* pass the error to the js executor function */
    return ex;
}
