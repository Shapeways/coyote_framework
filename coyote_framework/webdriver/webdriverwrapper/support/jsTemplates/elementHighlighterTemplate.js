/* Usage: replace all variables prefaced with '%' then execute file text as a string */

/* %x: the x-coordinate of the element */
/* %y: the y-coordinate of the element */
/* %width: the width of the element */
/* %height: the height of the element */

try {
    /* Remove existing webdriver messages */
    var highlightClass = 'webdriver-element-highlight';
    var existingHighlights = document.querySelectorAll("." + highlightClass);
    for (var i=0; i<existingHighlights.length; i++) {
        existingHighlights[i].parentNode.removeChild(existingHighlights[i]);
    }

    var highlight = document.createElement('div');

    highlight.style.position = 'fixed';
    highlight.style.border = '3px dotted red';

    try {
        highlight.style.left = '%xpx';
        highlight.style.top = '%ypx';
        highlight.style.width = '%widthpx';
        highlight.style.height = '%heightpx';
        highlight.style.zIndex = '2147483647';
    } catch (e) {
        highlight.innerHTML = 'Problem populating highlight element style variables. See source.';
    }

    highlight.className += highlightClass;

    var body = document.querySelector('body');
    body.appendChild(highlight);

    /* so that true will be passed to js executor function */
    return true;

} catch (ex) {
    /* pass the error to the js executor function */
    return ex;
}
