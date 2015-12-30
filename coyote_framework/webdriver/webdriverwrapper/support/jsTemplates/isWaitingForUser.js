
/* Checks if the webdriver paused radio button is ticked;
 * Return true if unchecked, false if checked, false if radio is not found
 */

try {
    var radioId = "webdriver-resume-radio";
    var radio = document.getElementById(radioId);

    if (radio && radio.checked) {
        return false;
    } else {
        return true;
    }

} catch (ex) {

    /* pass the error to the js function */
    return ex;
}