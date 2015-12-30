
/* Usage: replace all variables prefaced with '%' then execute file text as a string */

/* %message: the message to display on the page */


try {
    /* Remove existing webdriver messages */
    var messageClass = 'webdriver-test-error-message';
    var existingMessages = document.querySelectorAll("."+messageClass);
    for (var i=0; i<existingMessages.length; i++) {
        existingMessages[i].parentNode.removeChild(existingMessages[i]);
    }

    var message = 'No error message';

    try {
        /* Catch exceptions in case message is malformed or has unfriendly characters */
        message = '%message';
    } catch (e) {
        message = 'The error message was malformed';
    }

    var messageText = document.createElement('span');
    var body = document.querySelector('body');

    messageText.innerHTML = "" + message;

    messageText.style.top = '5px';
    messageText.style.left = '5px';
    messageText.style.margin = '20px';
    messageText.style.padding = '20px';
    messageText.style.color = 'red';
    messageText.style.fontSize = '20px';
    messageText.style.lineHeight = '30px';
    messageText.style.fontFamily = 'Arial';
    messageText.style.fontWeight = 'bold';
    messageText.style.position = 'fixed';
    messageText.style.zIndex = '2147483647';

    messageText.className += messageClass;
    body.appendChild(messageText);

    return true;

} catch (ex) {

    /* pass the error to the js function */
    return ex;
}