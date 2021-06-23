/*jshint esversion: 8 */

// declare variables
const websocketUrl = `ws://${window.location.hostname}:8000/ws`;
let songList = [];
let oldLenSongList = 0;
let lenSongList = 0;
let deleteSongEmpty = false;
let deleteNoPlaying = false;

// declares const class name
const containerClass = "columns is-mobile is-size-4 text-bolder mb-3";
const listClass = "column has-text-centered p-0";
const nameClass = "column is-three-fifths p-0 nowrap-text";
const scoreClass = "column is-one-fifths has-text-centered p-0";
const linkClass = "column is-one-fifths has-text-centered p-0";
const playButton = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pg0gPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDE2LjAuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgLS0+DSA8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4iICJodHRwOi8vd3d3LnczLm9yZy9HcmFwaGljcy9TVkcvMS4xL0RURC9zdmcxMS5kdGQiPg0gPHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJDYXBhXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4Ig0gd2lkdGg9IjQwOC4yMjFweCIgaGVpZ2h0PSI0MDguMjIxcHgiIHZpZXdCb3g9IjAgMCA0MDguMjIxIDQwOC4yMjEiIHN0eWxlPSJlbmFibGUtYmFja2dyb3VuZDpuZXcgMCAwIDQwOC4yMjEgNDA4LjIyMTsiDSB4bWw6c3BhY2U9InByZXNlcnZlIj4NIDxnPg0gPGc+DSA8cGF0aCBkPSJNMjA0LjExLDBDOTEuMzg4LDAsMCw5MS4zODgsMCwyMDQuMTExYzAsMTEyLjcyNSw5MS4zODgsMjA0LjExLDIwNC4xMSwyMDQuMTFjMTEyLjcyOSwwLDIwNC4xMS05MS4zODUsMjA0LjExLTIwNC4xMQ0gQzQwOC4yMjEsOTEuMzg4LDMxNi44MzksMCwyMDQuMTEsMHogTTI4Ni41NDcsMjI5Ljk3MWwtMTI2LjM2OCw3Mi40NzFjLTE3LjAwMyw5Ljc1LTMwLjc4MSwxLjc2My0zMC43ODEtMTcuODM0VjE0MC4wMTINIGMwLTE5LjYwMiwxMy43NzctMjcuNTc1LDMwLjc4MS0xNy44MjdsMTI2LjM2OCw3Mi40NjZDMzAzLjU1MSwyMDQuNDAzLDMwMy41NTEsMjIwLjIxNywyODYuNTQ3LDIyOS45NzF6Ii8+DSA8L2c+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8Zz4NIDwvZz4NIDxnPg0gPC9nPg0gPGc+DSA8L2c+DSA8L3N2Zz4N";

// generate song list element
const generateSongList = (songList) =>{
    var songListElement = document.getElementById("list-title");

    for(i = 0; i < oldLenSongList; i++){
        index = i + 1;
        var containerElement = document.getElementById(`container${index}`);
        containerElement.parentNode.removeChild(containerElement);
    }

    if(lenSongList > 0){
        let index = 1;
        songList.forEach(songData => {
            var containerElement = document.createElement("div");
            containerElement.className = containerClass;
            containerElement.id = `container${index}`;

            var listElement = document.createElement("div");
            listElement.className = listClass;
            listElement.innerHTML = `[${index.toString()}]`;

            var nameElement = document.createElement("div");
            nameElement.className = nameClass;
            nameElement.innerHTML = songData.songName;
            nameElement.id = `name${index}`;

            var voteElement = document.createElement("div");
            voteElement.className = scoreClass;
            voteElement.innerHTML = `${songData.vote.toString()} pts`;
            voteElement.id = `vote${index}`;

            var selElement = document.createElement("div");
            selElement.className = linkClass;
            selElement.innerHTML = '<a href="javascript:;" onclick="selectSong(\''+songData.songName+'\')">Select</a>';
            selElement.id = `sel${index}`;

            var delElement = document.createElement("div");
            delElement.className = linkClass;
            delElement.innerHTML = '<a href="javascript:;" onclick="deleteSong(\''+songData.songName+'\')">Delete</a>';
            delElement.id = `del${index}`;

            songListElement.appendChild(containerElement);
            containerElement.appendChild(listElement);
            containerElement.appendChild(nameElement);
            containerElement.appendChild(voteElement);
            containerElement.appendChild(selElement);
            containerElement.appendChild(delElement);
            index++;
        });
    }
};

const generateSongListEmpty = (delEmpty) =>{
    var songListElement = document.getElementById("list-title");
    var noElement = document.getElementById("emptylist");
    if(noElement === null && !delEmpty){
        noElement = document.createElement("div");
        noElement.className = containerClass;
        noElement.id = "emptylist";

        var nosongElement = document.createElement("div");
        nosongElement.className = "column has-text-centered p-0";
        nosongElement.innerHTML = "ขอเพลง !sr กันเข้ามา";

        songListElement.appendChild(noElement);
        noElement.appendChild(nosongElement);
    }else if(noElement !== null && delEmpty){
        noElement.parentNode.removeChild(noElement);
    }
};

// generate now playing element
const generateNowPlaying = (song) =>{
    var nowPlayingListElement = document.getElementById("nowplaying-title");
    var containerElement = document.getElementById("nowplaying");

    if(containerElement !== null){
        containerElement.parentNode.removeChild(containerElement);
    }

    if(song !== undefined){
        containerElement = document.createElement("div");
        containerElement.className = containerClass;
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
        nameElement.innerHTML = song.songName;
        nameElement.id = "nowplayingName";

        var voteElement = document.createElement("div");
        voteElement.className = scoreClass;
        voteElement.innerHTML = `${song.vote} pts`;
        voteElement.id = "nowplayingVote";

        var delElement = document.createElement("div");
        delElement.className = linkClass;
        delElement.innerHTML = "<a href='javascript:;' onclick=deleteNowPlaying()>Delete</a>";
        delElement.id = "delNowPlaying";

        nowPlayingListElement.appendChild(containerElement);
        containerElement.appendChild(imgElement);
        containerElement.appendChild(nameElement);
        containerElement.appendChild(voteElement);
        containerElement.appendChild(delElement);
    }
};

const generateNowPlayingEmpty = (delEmpty) =>{
    var nowPlayingListElement = document.getElementById("nowplaying-title");
    var noElement = document.getElementById("noplaying");
    if(noElement === null && !delEmpty){
        noElement = document.createElement("div");
        noElement.className = containerClass;
        noElement.id = "noplaying";
    
        var nosongElement = document.createElement("div");
        nosongElement.className = "column has-text-centered p-0";
        nosongElement.innerHTML = "ยังไม่มีเพลงที่เล่นน้า";
    
        nowPlayingListElement.appendChild(noElement);
        noElement.appendChild(nosongElement);
    }else if(noElement !== null && delEmpty){
        noElement.parentNode.removeChild(noElement);
    }
};

// api function
const selectSong = (songName) =>{
    const songKey = songName.toLowerCase();
    const url = `http://${window.location.hostname}:8000/api/v1/select`;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.send(JSON.stringify({
        "songKey": songKey
    }));
};

const deleteSong = (songName) =>{
    const songKey = songName.toLowerCase();
    const url = `http://${window.location.hostname}:8000/api/v1/del`;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.send(JSON.stringify({
        "songKey": songKey
    }));
};

const deleteNowPlaying = () =>{
    const url = `http://${window.location.hostname}:8000/api/v1/rem`;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.send(JSON.stringify({
        "confirm": true
    }));
};

const ws = new WebSocket(websocketUrl);
ws.onopen = () =>{
    ws.send("Handshake");
};
ws.addEventListener("message", (event) =>{
    response = (JSON.parse(event.data));
    songList = response.songlist;
    nowPlaying = response.nowplaying;

    lenSongList = songList.length;
    if(lenSongList > 0){
        deleteSongEmpty = true;
    }else{
        deleteSongEmpty = false;
    }
    generateSongList(songList);
    generateSongListEmpty(deleteSongEmpty);
    oldLenSongList = lenSongList;

    if(nowPlaying === undefined){
        deleteNoPlaying = false;
    }else{
        deleteNoPlaying = true;
    }
    generateNowPlaying(nowPlaying);
    generateNowPlayingEmpty(deleteNoPlaying);
});

const isElementOverflowing = (element) =>{
    var overflowX = element.offsetWidth < element.scrollWidth;
    return(overflowX);
};

const wrapContentInMarquee = (element) =>{
    var marquee = document.createElement('div'),
    contents = element.innerText;

    marquee.innerText = contents;
    marquee.className = 'sliding-text';
    element.innerHTML = '';
    element.appendChild(marquee);
};
