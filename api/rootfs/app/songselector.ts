import { broadcastEvents } from "./wsServer.ts"

// declare type of Song
interface Song {
    songKey: string,
    songName: string,
    vote: number,
    ts: Date
}

// declare type of song request
interface Req {
    songKey: string
}

// declare type of list clear request
interface Confirm {
    confirm: boolean
}

// declare nowPlaying variable
let nowPlaying: Song = {
    songKey: "",
    songName: "",
    vote: 0,
    ts: new Date()
}

// declare songList variable
let songList: Song[] = []

// function to return sort song list
const sortSongList = (songList: Song[]): Song[] =>{
    var sortedList: Song[] = songList.sort((vote1, vote2) =>{
        if(vote1.vote > vote2.vote) return -1
        if(vote1.vote < vote2.vote) return 1
    
        if(vote1.ts < vote2.ts) return -1
        if(vote1.ts > vote2.ts) return 1
    
        return 0
    })
    return sortedList
}

// function to response sorted song list
export const preparedResponse = () =>{
    const sortedSongList = sortSongList(songList)
    let response = {}
    if(nowPlaying.songName !== ""){
        response = {
            success: true,
            songlist: sortedSongList,
            nowplaying: nowPlaying
        }
    }else{
        response = {
            success: true,
            songlist: sortedSongList,
        }
    }
    broadcastEvents(JSON.stringify(response))
    return response
}

export const queryList = () =>{
    const response = preparedResponse()
    const status = 200
    return {status, response}
}

export const songVote = (song: Song) =>{
    let totalVote = 0
    const index: number = songList.findIndex(i => i.songKey === song.songKey.toLowerCase())
    if(index !== -1){
        songList[index].vote += song.vote
        totalVote = songList[index].vote
    }else{
        song.ts = new Date(song.ts)
        song.songKey = song.songKey.toLowerCase()
        songList.push(song)
        totalVote = 1
    }
    const voteObj = {
        songname: song.songName,
        songvote: totalVote
    }
    let response = preparedResponse()
    response = {...response, ...voteObj}
    return response
}

export const selectSong = (req: Req) =>{
    const index: number = songList.findIndex(i => i.songKey === req.songKey.toLowerCase())
    let status = 100
    if(index !== -1){
        nowPlaying = songList[index]
        songList = songList.filter(i => i.songKey !== req.songKey.toLowerCase())
        status = 200
    }else{
        console.log("[SEL] not found "+req.songKey)
        status = 404
    }
    const response = preparedResponse()
    return {status, response}
}

export const deleteSong = (req: Req) =>{
    const index: number = songList.findIndex(i => i.songKey === req.songKey.toLowerCase())
    let status = 100
    if(index !== -1){
        songList = songList.filter(i => i.songKey !== req.songKey.toLowerCase())
        status = 200
    }else{
        console.log("[DEL] not found "+req.songKey)
        status = 404
    }
    const response = preparedResponse()
    return {status, response}
}

export const clearList = (req: Confirm) =>{
    let status = 100
    if(req.confirm){
        songList = []
        status = 200
    }else{
        status = 404
    }
    const response = preparedResponse()
    return {status, response}
}

export const removeNowPlaying = (req: Confirm) =>{
    let status = 100
    if(req.confirm){
        nowPlaying = {
            songKey: "",
            songName: "",
            vote: 0,
            ts: new Date()
        }
        status = 200
    }else{
        status = 404
    }
    const response = preparedResponse()
    return {status, response}
}
