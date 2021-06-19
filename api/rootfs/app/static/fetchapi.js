/*jshint esversion: 8 */

// declare variables
const websocketUrl = `ws://${window.location.hostname}:8000/ws`;
let songList = [];
let nowPlaying = "nothing";
let oldSongList = [];
let oldNowPlaying = [];

// declares const class name
const containerClass = "columns is-mobile is-size-4 text-bolder mb-3";
const listClass = "column has-text-centered p-0";
const nameClass = "column is-three-fifths p-0 nowrap-text";
const scoreClass = "column is-one-quarter has-text-centered p-0";
const playButton = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pg0gPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDE2LjAuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgLS0+DSA8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4iICJodHRwOi8vd3d3LnczLm9yZy9HcmFwaGljcy9TVkcvMS4xL0RURC9zdmcxMS5kdGQiPg0gPHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJDYXBhXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4Ig0gd2lkdGg9IjQwOC4yMjFweCIgaGVpZ2h0PSI0MDguMjIxcHgiIHZpZXdCb3g9IjAgMCA0MDguMjIxIDQwOC4yMjEiIHN0eWxlPSJlbmFibGUtYmFja2dyb3VuZDpuZXcgMCAwIDQwOC4yMjEgNDA4LjIyMTsiDSB4bWw6c3BhY2U9InByZXNlcnZlIj4NIDxnPg0gPGc+DSA8cGF0aCBmaWxsPSIjRkZGRkZGIiBkPSJNMjA0LjExLDBDOTEuMzg4LDAsMCw5MS4zODgsMCwyMDQuMTExYzAsMTEyLjcyNSw5MS4zODgsMjA0LjExLDIwNC4xMSwyMDQuMTFjMTEyLjcyOSwwLDIwNC4xMS05MS4zODUsMjA0LjExLTIwNC4xMQ0gQzQwOC4yMjEsOTEuMzg4LDMxNi44MzksMCwyMDQuMTEsMHogTTI4Ni41NDcsMjI5Ljk3MWwtMTI2LjM2OCw3Mi40NzFjLTE3LjAwMyw5Ljc1LTMwLjc4MSwxLjc2My0zMC43ODEtMTcuODM0VjE0MC4wMTINIGMwLTE5LjYwMiwxMy43NzctMjcuNTc1LDMwLjc4MS0xNy44MjdsMTI2LjM2OCw3Mi40NjZDMzAzLjU1MSwyMDQuNDAzLDMwMy41NTEsMjIwLjIxNywyODYuNTQ3LDIyOS45NzF6Ii8+DSA8L2c+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8L3N2Zz4N";

// generate song list element
function generateSongList(songList, index){
    if(songList[index - 1] === undefined){
        songName = "No Song";
        vote = 0;
        modClass = " is-hidden";
    }else{
        songName = songList[index - 1].songName;
        vote = songList[index - 1].vote;
        modClass = "";
    }

    var containerElement = document.createElement("div");
    containerElement.className = containerClass + modClass;
    containerElement.id = "container"+index;

    var listElement = document.createElement("div");
    listElement.className = listClass;
    listElement.innerHTML = "["+index.toString()+"]";

    var nameElement = document.createElement("div");
    nameElement.className = nameClass;
    nameElement.innerHTML = songName;
    nameElement.id = "name"+index;

    var voteElement = document.createElement("div");
    voteElement.className = scoreClass;
    voteElement.innerHTML = vote.toString()+" pts";
    voteElement.id = "vote"+index;

    var songListElement = document.getElementById("list-title");
    songListElement.appendChild(containerElement);
    containerElement.appendChild(listElement);
    containerElement.appendChild(nameElement);
    containerElement.appendChild(voteElement);

    if(index === 5){
        if(songList.length === 0){
            modClass = "";
        }else{
            modClass = " is-hidden";
        }
        var noElement = document.createElement("div");
        noElement.className = containerClass + modClass;
        noElement.classList.remove("mb-3");
        noElement.id = "emptylist";

        var nosongElement = document.createElement("div");
        nosongElement.className = "column has-text-centered p-0";
        nosongElement.innerHTML = "ขอเพลง !sr กันเข้ามา";

        songListElement.appendChild(noElement);
        noElement.appendChild(nosongElement);
    }
}

// generate now playing element
function generateNowPlaying(song){
    var nowPlayingListElement = document.getElementById("nowplaying-title");
    if(song === "nothing" || song === undefined){
        modnoClass = "";
        modSongClass = " is-hidden";
        songName = "No Song";
        vote = 0;
    }else{
        modnoClass = " is-hidden";
        modSongClass = "";
        songName = song.songName;
        vote = song.vote;
    }
    var containerElement = document.createElement("div");
    containerElement.className = containerClass + modSongClass;
    containerElement.id = "nowplaying";

    var imgElement = document.createElement("div");
    imgElement.className = listClass;
    var svgElement = document.createElement("img");
    svgElement.setAttribute("width", "36");
    svgElement.setAttribute("height", "36");
    svgElement.setAttribute("stroke", "white");
    svgElement.src = `data:image/svg+xml;base64,${playButton}`;
    imgElement.appendChild(svgElement);

    var nameElement = document.createElement("div");
    nameElement.className = nameClass;
    nameElement.innerHTML = songName;
    nameElement.id = "nowplayingName";

    var voteElement = document.createElement("div");
    voteElement.className = scoreClass;
    voteElement.innerHTML = vote+" pts";
    voteElement.id = "nowplayingVote";
    
    nowPlayingListElement.appendChild(containerElement);
    containerElement.appendChild(imgElement);
    containerElement.appendChild(nameElement);
    containerElement.appendChild(voteElement);

    var noElement = document.createElement("div");
    noElement.className = containerClass + modnoClass;
    noElement.id = "noplaying";

    var nosongElement = document.createElement("div");
    nosongElement.className = "column has-text-centered p-0";
    nosongElement.innerHTML = "ยังไม่มีเพลงที่เล่นน้า";

    nowPlayingListElement.appendChild(noElement);
    noElement.appendChild(nosongElement);
}

// refresh song list
function refreshSongList(songList){
    for(i = 0; i < 5; i++){
        index = i + 1;
        var containerElement = document.getElementById("container"+index.toString());
        var nameElement = document.getElementById("name" + index.toString());
        var voteElement = document.getElementById("vote" + index.toString());
        if(songList[i] !== undefined){
            nameElement.innerHTML = songList[i].songName;
            voteElement.innerHTML = songList[i].vote.toString()+" pts";
            if(containerElement.classList.contains("is-hidden")){
                containerElement.classList.remove("is-hidden");
            }
        }else{
            nameElement.innerHTML = "No Song";
            voteElement.innerHTML = "0 pts";
            if(!(containerElement.classList.contains("is-hidden"))){
                containerElement.classList.add("is-hidden");
            }
        }
        if(isElementOverflowing(nameElement)){
            wrapContentInMarquee(nameElement);
        }
    }
    var noElement = document.getElementById("emptylist");
    if(songList.length === 0){
        if(noElement.classList.contains("is-hidden")){
            noElement.classList.remove("is-hidden");
        }
    }else{
        if(!(noElement.classList.contains("is-hidden"))){
            noElement.classList.add("is-hidden");
        }
    }
}

// refresh nowplaying
function refreshNowPlaying(song){
    var containerElement = document.getElementById("nowplaying");
    var nameElement = document.getElementById("nowplayingName");
    var voteElement = document.getElementById("nowplayingVote");
    var noElement = document.getElementById("noplaying");
    if(song !== undefined){
        nameElement.innerHTML = song.songName;
        voteElement.innerHTML = song.vote.toString()+" pts";
        if(containerElement.classList.contains("is-hidden")){
            containerElement.classList.remove("is-hidden");
        }
        if(!(noElement.classList.contains("is-hidden"))){
            noElement.classList.add("is-hidden");
        }
    }else{
        nameElement.innerHTML = "No Song";
        voteElement.innerHTML = "0 pts";
        if(!(containerElement.classList.contains("is-hidden"))){
            containerElement.classList.add("is-hidden");
        }
        if(noElement.classList.contains("is-hidden")){
            noElement.classList.remove("is-hidden");
        }
    }
    if(isElementOverflowing(nameElement)){
        wrapContentInMarquee(nameElement);
    }
}

const ws = new WebSocket(websocketUrl);
ws.onopen = function(){
    ws.send("Handshake");
};
ws.addEventListener("message", function(event){
    response = (JSON.parse(event.data));
    songList = response.songlist;
    nowPlaying = response.nowplaying;
    refreshSongList(songList);
    refreshNowPlaying(nowPlaying);
});

for (i = 0; i < 5; i++){
    generateSongList(songList, i + 1);
}
generateNowPlaying(nowPlaying);

function isElementOverflowing(element){
    var overflowX = element.offsetWidth < element.scrollWidth;
    return(overflowX);
}

function wrapContentInMarquee(element){
    var marquee = document.createElement('div'),
    contents = element.innerText;

    marquee.innerText = contents;
    marquee.className = 'sliding-text';
    element.innerHTML = '';
    element.appendChild(marquee);
}
