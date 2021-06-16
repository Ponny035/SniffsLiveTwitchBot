/*jshint esversion: 8 */

// declare variables
const fetchUrl = "http://songfeed.picturo.us:8000/api/v1/songlist";
// const fetchUrl = "http://localhost:8000/api/v1/songlist";
let songList = [];
let nowPlaying = {};
let oldSongList = [];
let oldNowPlaying = [];

// declare fetch function
async function getSongList(url){
    try{
        let response = await fetch(url, {
            mode: 'cors',
            cache: 'no-cache'
        });
        return await response.json();
    }catch(error){
        console.log(error);
    }
}

// declares const class name
const containerClass = "columns is-mobile is-size-5 has-text-weight-semibold mb-3";
const listClass = "column has-text-centered p-0";
const nameClass = "column is-three-fifths p-0 nowrap-text";
const scoreClass = "column is-one-quarter has-text-centered p-0";

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
    voteElement.innerHTML = vote.toString()+" คะแนน";
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
        nosongElement.innerHTML = "ยังไม่มีเพลง ขอเพลง !sr กันเข้ามา";

        songListElement.appendChild(noElement);
        noElement.appendChild(nosongElement);
    }
}

// generate now playing element
function generateNowPlaying(song){
    var nowPlayingListElement = document.getElementById("nowplaying-title");

    if(song !== undefined){
        modnoClass = " is-hidden";
        modSongClass = "";
        songName = song.songName;
        vote = song.vote;
    }else{
        modnoClass = "";
        modSongClass = " is-hidden";
        songName = "No Song";
        vote = 0;
    }
    var containerElement = document.createElement("div");
    containerElement.className = containerClass + modSongClass;
    containerElement.id = "nowplaying";

    var imgElement = document.createElement("div");
    imgElement.className = listClass;
    var pngElement = document.createElement("img");
    pngElement.setAttribute("width", "24");
    pngElement.setAttribute("height", "24");
    pngElement.src = "/play.png";
    imgElement.appendChild(pngElement);

    var nameElement = document.createElement("div");
    nameElement.className = nameClass;
    nameElement.innerHTML = songName;
    nameElement.id = "nowplayingName";

    var voteElement = document.createElement("div");
    voteElement.className = scoreClass;
    voteElement.innerHTML = vote+" คะแนน";
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
            voteElement.innerHTML = songList[i].vote.toString()+" คะแนน";
            if(containerElement.classList.contains("is-hidden")){
                containerElement.classList.remove("is-hidden");
            }
        }else{
            nameElement.innerHTML = "No Song";
            voteElement.innerHTML = "0 คะแนน";
            if(!(containerElement.classList.contains("is-hidden"))){
                containerElement.classList.add("is-hidden");
            }
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
        voteElement.innerHTML = song.vote.toString()+" คะแนน";
        if(containerElement.classList.contains("is-hidden")){
            containerElement.classList.remove("is-hidden");
        }
        if(!(noElement.classList.contains("is-hidden"))){
            noElement.classList.add("is-hidden");
        }
    }else{
        nameElement.innerHTML = "No Song";
        voteElement.innerHTML = "0 คะแนน";
        if(!(containerElement.classList.contains("is-hidden"))){
            containerElement.classList.add("is-hidden");
        }
        if(noElement.classList.contains("is-hidden")){
            noElement.classList.remove("is-hidden");
        }
    }
}

// fetch first list
getSongList(fetchUrl).then(response =>{
    songList = response.songlist;
    nowPlaying = response.nowplaying;
    for (i = 0; i < 5; i++){
        generateSongList(songList, i + 1);
    }
    generateNowPlaying(nowPlaying);
});

// promise fetch interval
var promise = Promise.resolve(true);

setInterval(function(){
    promise = promise.then(getSongList(fetchUrl).then(response =>{
        songList = response.songlist;
        nowPlaying = response.nowplaying;
        // console.log(songList);
        // console.log(nowPlaying);
        refreshSongList(songList);
        refreshNowPlaying(nowPlaying);
    }));
}, 1000);
