import { getTimestamp } from "../functions/gettimestamp.ts"
import { Song, Req, Confirm, VoteObj } from "../interfaces/Songselector.ts"
import { socketSend } from "../routes/wsServer.ts"

let songList: Song[] = []

let nowPlaying: Song = {
    songKey: "",
    songName: "",
    vote: 0,
    ts: new Date()
}

const sortSongList = (songList: Song[]): Song[] =>{
    const sortedList: Song[] = songList.sort((vote1, vote2) =>{
        if(vote1.vote > vote2.vote) return -1
        if(vote1.vote < vote2.vote) return 1

        if(vote1.ts < vote2.ts) return -1
        if(vote1.ts > vote2.ts) return 1
        
        return 0
    })
    return sortedList
}

const preparedResponse = () =>{
    const sortedSongList = sortSongList(songList)
    let response = {
        success: true,
        songlist: sortedSongList
    }
    if(nowPlaying.songName !== ""){
        Object.assign(response, {nowplaying: nowPlaying})
    }
    socketSend("songfeed", JSON.stringify(response))
    return response
}

const handleSongVote = (votedSong: Song): VoteObj =>{
    let totalVote: number = 0
    const index: number = songList.findIndex(i => i.songKey === votedSong.songKey.toLowerCase())
    if(index !== -1){
        songList[index].vote += votedSong.vote
        totalVote = songList[index].vote
    }else{
        votedSong.ts = new Date(votedSong.ts)
        votedSong.songKey = votedSong.songKey.toLowerCase()
        songList.push(votedSong)
        totalVote = 1
    }
    const voteObj: VoteObj = {
        songname: votedSong.songName,
        songvote: totalVote
    }
    return voteObj
}

const handleSongDelete = (req: Req) =>{
    songList = songList.filter(i => i.songKey !== req.songKey.toLowerCase())
}

const handleListClear = (req: Confirm) =>{
    if(req.confirm){
        songList = []
    }
}

const setNowPlaying = (req: Req, index: number) =>{
    nowPlaying = songList[index]
    songList = songList.filter(i => i.songKey !== req.songKey.toLowerCase())
}

const resetNowPlaying = (req: Confirm) =>{
    if(req.confirm){
        nowPlaying = {
            songKey: "",
            songName: "",
            vote: 0,
            ts: new Date()
        }
    }
}

export const firstHandShake = () =>{
    preparedResponse()
}

export default {
    queryList: ({ response }: { response: any }) =>{
        response.status = 200
        response.body = preparedResponse()
    },
    songVote: async({ request, response }: { request: any, response: any }) =>{
        if(!request.hasBody){
            response.status = 404
            response.body = {
                success: false,
                msg: "no data input"
            }
            return
        }
        const body = request.body()
        const votedSong: Song = await body.value
        const voteObj = handleSongVote(votedSong)
        response.status = 200
        response.body = {...preparedResponse(), ...voteObj}
    },
    selectSong: async({ request, response }: { request: any, response: any }) =>{
        if(!request.hasBody){
            response.status = 404
            response.body = {
                success: false,
                msg: "no data input"
            }
            return
        }
        const body = request.body()
        const req: Req = await body.value
        const index: number = songList.findIndex(i => i.songKey === req.songKey.toLowerCase())
        if(index === -1){
            response.status = 404
            console.log(`[_API] [${getTimestamp()}] Song selection with ${req.songKey} not found`)
            return
        }
        setNowPlaying(req, index)
        response.status = 200
        response.body = preparedResponse()
    },
    deleteSong: async({ request, response }: { request: any, response: any }) =>{
        if(!request.hasBody){
            response.status = 404
            response.body = {
                success: false,
                msg: "no data input"
            }
            return
        }
        const body = request.body()
        const req: Req = await body.value
        const index: number = songList.findIndex(i => i.songKey === req.songKey.toLowerCase())
        if(index === -1){
            response.status = 404
            console.log(`[_API] [${getTimestamp()}] Song deletion with ${req.songKey} not found`)
            return
        }
        handleSongDelete(req)
        response.status = 200
        response.body = preparedResponse()
    },
    clearList: async({ request, response }: { request: any, response: any }) =>{
        if(!request.hasBody){
            response.status = 404
            response.body = {
                success: false,
                msg: "no data input"
            }
            return
        }
        const body = request.body()
        const req: Confirm = await body.value
        handleListClear(req)
        response.status = 200
        response.body = preparedResponse()
    },
    removeNowPlaying: async({ request, response }: { request: any, response: any }) =>{
        if(!request.hasBody){
            response.status = 404
            response.body = {
                success: false,
                msg: "no data input"
            }
            return
        }
        const body = request.body()
        const req: Confirm = await body.value
        resetNowPlaying(req)
        response.status = 200
        response.body = preparedResponse()
    },
}
