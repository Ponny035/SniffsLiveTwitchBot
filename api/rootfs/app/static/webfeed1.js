/*jshint esversion: 11 */

const websocketUrl = `ws://${window.location.hostname}:8000/ws`;

const messageTimeout = 5000;

const addNotificationFeed = (message, timeout = messageTimeout) => {
    const parentContainerElement = document.getElementById("base-container");

    const containerElement = document.createElement("div");
    containerElement.className = "pt-2";
    containerElement.classList.add("fadein");

    const baseSpanElement = document.createElement("span");
    baseSpanElement.className = "icon-text";
    baseSpanElement.innerHTML = message;

    containerElement.appendChild(baseSpanElement);
    parentContainerElement.appendChild(containerElement);

    setTimeout(() => {
        containerElement.classList.remove("fadein");
        containerElement.classList.add("fadeout");
        setTimeout(() => {
            parentContainerElement.removeChild(containerElement);
        }, 500);
    }, timeout);
};

const ws = new WebSocket(websocketUrl);
ws.onopen = () =>{
    ws.send("webfeedHandshake");
};
ws.addEventListener("message", function(event){
    const response = JSON.parse(event.data);
    const message = response.message;
    const timeout = response?.timeout;
    addNotificationFeed(message, timeout);
});