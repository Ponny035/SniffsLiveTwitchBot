/*jshint esversion: 8 */

const websocketUrl = `ws://${window.location.hostname}:8000/ws`;

const messageTimeout = 5000;
// const defaultIcon = "icon";
// const defaultTagName = "tag is-info has-text-weight-bold";
// const defaultTagViewer = "tag is-primary has-text-weight-bold";
// const testIcon1 = "fas fa-hand-holding-usd";
// const testIcon2 = "fas fa-level-up-alt";

const addNotificationFeed = (webfeed) => {
    const parentContainerElement = document.getElementById("base-container");

    const containerElement = document.createElement("div");
    containerElement.className = "pt-2";
    containerElement.classList.add("fadein");

    const baseSpanElement = document.createElement("span");
    baseSpanElement.className = "icon-text";
    baseSpanElement.innerHTML = webfeed;

    // const tagSpanElement = document.createElement("span");
    // tagSpanElement.className = defaultTagName;
    // tagSpanElement.innerHTML = username;

    // const textSpanElement = document.createElement("span");
    // textSpanElement.className = "text-white";

    // const icon1BaseElement = document.createElement("span");
    // icon1BaseElement.className = defaultIcon;
    // const icon1Element = document.createElement("i");
    // icon1Element.className = testIcon1;
    // icon1BaseElement.appendChild(icon1Element);

    // textSpanElement.appendChild(icon1BaseElement);
    
    // baseSpanElement.appendChild(tagSpanElement);
    // baseSpanElement.appendChild(textSpanElement);

    containerElement.appendChild(baseSpanElement);
    parentContainerElement.appendChild(containerElement);

    setTimeout(() => {
        containerElement.classList.remove("fadein");
        containerElement.classList.add("fadeout");
        setTimeout(() => {
            parentContainerElement.removeChild(containerElement);
        }, 500);
    }, messageTimeout);
};

const ws = new WebSocket(websocketUrl);
ws.onopen = () =>{
    ws.send("webfeedHandshake");
};
ws.addEventListener("message", function(event){
    const response = event.data;
    addNotificationFeed(response);
});