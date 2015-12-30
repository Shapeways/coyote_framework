
/* Deletes all found elements with a specified selector */

try {
    var selector = "%selector";

    var allElements = document.querySelectorAll(selector);

    while (allElements.length > 0) {
        var firstElement = allElements[0];
        firstElement.parentElement.removeChild(firstElement);
    }

    return true;

} catch (ex) {

    /* pass the error to the js function */
    return ex;
}