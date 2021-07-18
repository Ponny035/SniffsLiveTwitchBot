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
const playButton = "fas fa-play-circle";

// generate song list element
const generateSongList = (songList) =>{
    const songListElement = document.getElementById("list-title");

    for(i = 0; i < oldLenSongList; i++){
        index = i + 1;
        const containerElement = document.getElementById(`container${index}`);
        containerElement.parentNode.removeChild(containerElement);
    }

    if(lenSongList > 0){
        let index = 1;
        songList.forEach(songData =>{
            const containerElement = document.createElement("div");
            containerElement.className = containerClass;
            containerElement.id = `container${index}`;

            const listElement = document.createElement("div");
            listElement.className = listClass;
            listElement.innerHTML = `[${index.toString()}]`;

            const nameElement = document.createElement("div");
            nameElement.className = nameClass;
            nameElement.innerHTML = songData.songName;
            nameElement.id = `name${index}`;

            const voteElement = document.createElement("div");
            voteElement.className = scoreClass;
            voteElement.innerHTML = `${songData.vote.toString()} pts`;
            voteElement.id = `vote${index}`;

            const selElement = document.createElement("div");
            selElement.className = linkClass;
            selElement.innerHTML = `<a href="javascript:;" onclick="selectSong(${index})">Select</a>`;
            selElement.id = `sel${index}`;

            const delElement = document.createElement("div");
            delElement.className = linkClass;
            delElement.innerHTML = `<a href="javascript:;" onclick="deleteSong(${index})">Delete</a>`;
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
    const songListElement = document.getElementById("list-title");
    let noElement = document.getElementById("emptylist");
    if(noElement === null && !delEmpty){
        noElement = document.createElement("div");
        noElement.className = containerClass;
        noElement.id = "emptylist";

        const nosongElement = document.createElement("div");
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
    const nowPlayingListElement = document.getElementById("nowplaying-title");
    let containerElement = document.getElementById("nowplaying");

    if(containerElement !== null){
        containerElement.parentNode.removeChild(containerElement);
    }

    if(song !== undefined){
        containerElement = document.createElement("div");
        containerElement.className = containerClass;
        containerElement.id = "nowplaying";

        const imgElement = document.createElement("div");
        imgElement.className = listClass;
        const spanElement = document.createElement("span");
        spanElement.className = "icon";
        const playElement = document.createElement("i");
        playElement.className = playButton;
        spanElement.appendChild(playElement);
        imgElement.appendChild(spanElement);

        const nameElement = document.createElement("div");
        nameElement.className = nameClass;
        nameElement.innerHTML = song.songName;
        nameElement.id = "nowplayingName";

        const voteElement = document.createElement("div");
        voteElement.className = scoreClass;
        voteElement.innerHTML = `${song.vote} pts`;
        voteElement.id = "nowplayingVote";

        const delElement = document.createElement("div");
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
    const nowPlayingListElement = document.getElementById("nowplaying-title");
    let noElement = document.getElementById("noplaying");
    if(noElement === null && !delEmpty){
        noElement = document.createElement("div");
        noElement.className = containerClass;
        noElement.id = "noplaying";
    
        const nosongElement = document.createElement("div");
        nosongElement.className = "column has-text-centered p-0";
        nosongElement.innerHTML = "ยังไม่มีเพลงที่เล่นน้า";
    
        nowPlayingListElement.appendChild(noElement);
        noElement.appendChild(nosongElement);
    }else if(noElement !== null && delEmpty){
        noElement.parentNode.removeChild(noElement);
    }
};

// api function
const selectSong = (songIndex) =>{
    const songKey = songList[Number(songIndex) - 1].songKey;
    const url = `http://${window.location.hostname}:8000/api/v1/select`;

    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.send(JSON.stringify({
        "songKey": songKey
    }));
};

const deleteSong = (songIndex) =>{
    const songKey = songList[Number(songIndex) - 1].songKey;
    const url = `http://${window.location.hostname}:8000/api/v1/del`;

    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.send(JSON.stringify({
        "songKey": songKey
    }));
};

const deleteNowPlaying = () =>{
    const url = `http://${window.location.hostname}:8000/api/v1/rem`;

    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.send(JSON.stringify({
        "confirm": true
    }));
};

const ws = new WebSocket(websocketUrl);
ws.onopen = () =>{
    ws.send("songfeedHandshake");
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
    const overflowX = element.offsetWidth < element.scrollWidth;
    return(overflowX);
};

const wrapContentInMarquee = (element) =>{
    const marquee = document.createElement('div'),
    contents = element.innerText;

    marquee.innerText = contents;
    marquee.className = 'sliding-text';
    element.innerHTML = '';
    element.appendChild(marquee);
};
