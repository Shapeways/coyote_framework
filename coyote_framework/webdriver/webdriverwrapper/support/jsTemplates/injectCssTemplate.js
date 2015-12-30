/* Injects css into the  */

/* %message: the message to display on the page */


try {
    var cssRules = "%css";

    var styleNode = document.createElement('style');
    styleNode.type = "text/css";
    styleNode.className = "webdriver-injected"; /* Allow node to be found and removed */
    styleNode.innerHTML = cssRules;

    document.getElementsByTagName("head")[0].appendChild(styleNode);

    return true;

} catch (ex) {

    /* pass the error to the js function */
    return ex;
}