
/* Usage: replace all variables prefaced with '%' then execute file text as a string */

/* %message: the message to display on the page */


try {
    var selector = "%selector";
    var html = "%html";
    var element = document.querySelector(selector);
    element.insertAdjacentHTML('beforeend', html);

    return true;

} catch (ex) {

    /* pass the error to the js function */
    return ex;
}