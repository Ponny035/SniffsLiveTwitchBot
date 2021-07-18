/*jshint esversion: 8 */

// declare variables
const websocketUrl = `ws://${window.location.hostname}:8000/ws`;
let songList = [];
let nowPlaying = "nothing";

// declares const class name
const containerClass = "columns is-mobile is-size-4 text-bolder mb-3";
const listClass = "column has-text-centered p-0";
const nameClass = "column is-three-fifths p-0 nowrap-text";
const scoreClass = "column is-one-quarter has-text-centered p-0";
const playButton = "fas fa-play-circle";

// generate song list element
const generateSongList = (songList, index) =>{
    if(songList[index - 1] === undefined){
        songName = "No Song";
        vote = 0;
        modClass = " is-hidden";
    }else{
        songName = songList[index - 1].songName;
        vote = songList[index - 1].vote;
        modClass = "";
    }

    const containerElement = document.createElement("div");
    containerElement.className = containerClass + modClass;
    containerElement.id = `container${index}`;

    const listElement = document.createElement("div");
    listElement.className = listClass;
    listElement.innerHTML = `[${index.toString()}]`;

    const nameElement = document.createElement("div");
    nameElement.className = nameClass;
    nameElement.innerHTML = songName;
    nameElement.id = `name${index}`;

    const voteElement = document.createElement("div");
    voteElement.className = scoreClass;
    voteElement.innerHTML = `${vote.toString()} pts`;
    voteElement.id = `vote${index}`;

    const songListElement = document.getElementById("list-title");
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
        const noElement = document.createElement("div");
        noElement.className = containerClass + modClass;
        noElement.classList.remove("mb-3");
        noElement.id = "emptylist";

        const nosongElement = document.createElement("div");
        nosongElement.className = "column has-text-centered p-0";
        nosongElement.innerHTML = "ขอเพลง !sr กันเข้ามา";

        songListElement.appendChild(noElement);
        noElement.appendChild(nosongElement);
    }
};

// generate now playing element
const generateNowPlaying = (song) =>{
    const nowPlayingListElement = document.getElementById("nowplaying-title");
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
    const containerElement = document.createElement("div");
    containerElement.className = containerClass + modSongClass;
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
    nameElement.innerHTML = songName;
    nameElement.id = "nowplayingName";

    const voteElement = document.createElement("div");
    voteElement.className = scoreClass;
    voteElement.innerHTML = `${vote} pts`;
    voteElement.id = "nowplayingVote";
    
    nowPlayingListElement.appendChild(containerElement);
    containerElement.appendChild(imgElement);
    containerElement.appendChild(nameElement);
    containerElement.appendChild(voteElement);

    const noElement = document.createElement("div");
    noElement.className = containerClass + modnoClass;
    noElement.id = "noplaying";

    const nosongElement = document.createElement("div");
    nosongElement.className = "column has-text-centered p-0";
    nosongElement.innerHTML = "ยังไม่มีเพลงที่เล่นน้า";

    nowPlayingListElement.appendChild(noElement);
    noElement.appendChild(nosongElement);
};

// refresh song list
const refreshSongList = (songList) =>{
    for(i = 0; i < 5; i++){
        index = i + 1;
        const containerElement = document.getElementById(`container${index.toString()}`);
        const nameElement = document.getElementById(`name${index.toString()}`);
        const voteElement = document.getElementById(`vote${index.toString()}`);
        if(songList[i] !== undefined){
            nameElement.innerHTML = songList[i].songName;
            voteElement.innerHTML = `${songList[i].vote.toString()} pts`;
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
    const noElement = document.getElementById("emptylist");
    if(songList.length === 0){
        if(noElement.classList.contains("is-hidden")){
            noElement.classList.remove("is-hidden");
        }
    }else{
        if(!(noElement.classList.contains("is-hidden"))){
            noElement.classList.add("is-hidden");
        }
    }
};

// refresh nowplaying
const refreshNowPlaying = (song) =>{
    const containerElement = document.getElementById("nowplaying");
    const nameElement = document.getElementById("nowplayingName");
    const voteElement = document.getElementById("nowplayingVote");
    const noElement = document.getElementById("noplaying");
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
};

const ws = new WebSocket(websocketUrl);
ws.onopen = function(){
    ws.send("songfeedHandshake");
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
