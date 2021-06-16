import { Application, Router, send } from "https://deno.land/x/oak@v7.5.0/mod.ts"

const port = 8000
const app = new Application()
const router = new Router()

// Logger
app.use(async (ctx, next) =>{
    await next()
    const rt = ctx.response.headers.get("X-Response-Time")
    console.log(`${ctx.request.method} ${ctx.request.url} - ${rt}`)
})

// Timing
app.use(async (ctx, next) =>{
    const start = Date.now();
    await next()
    const ms = Date.now() - start
    ctx.response.headers.set("X-Response-Time", `${ms}ms`)
    ctx.response.headers.append("Access-Control-Allow-Origin", "*")
})

app.use(router.routes())
app.use(router.allowedMethods())

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
function sortSongList(songList: Song[]): Song[] {
    var sortedList: Song[] = songList.sort((vote1, vote2) =>{
        if(vote1.vote > vote2.vote) return -1
        if(vote1.vote < vote2.vote) return 1
    
        if(vote1.ts < vote2.ts) return -1
        if(vote1.ts > vote2.ts) return 1
    
        return 0
    })
    return sortedList
}

// @desc GET all sorted song list
router.get("/api/v1/songlist", ({response}: {response: any}) =>{
    const sortedSongList = sortSongList(songList)
    response.status = 200
    if(nowPlaying.songName !== ""){
        response.body = {
            success: true,
            songlist: sortedSongList,
            nowplaying: nowPlaying
        }
    }else{
        response.body = {
            success: true,
            songlist: sortedSongList
        }
    }
})

// @desc POST insert song / vote to song list
router.post("/api/v1/vote", async({request, response}: {request: any, response: any}) =>{
    if(request.hasBody){
        const body = request.body()
        const song: Song = await body.value
        let vote = 1
        let index: number | undefined = songList.findIndex(name => name.songKey === song.songKey)
        if(index !== -1){
            songList[index].vote += song.vote
            vote = songList[index].vote
        }else{
            song.ts = new Date(song.ts)
            songList.push(song)
            vote = 1
        }
        const sortedSongList = sortSongList(songList)
        response.status = 200
        if(nowPlaying.songName !== ""){
            response.body = {
                success: true,
                songname: song.songName,
                songvote: vote,
                songlist: sortedSongList,
                nowplaying: nowPlaying
            }
        }else{
            response.body = {
                success: true,
                songname: song.songName,
                songvote: vote,
                songlist: sortedSongList
            }
        }
        console.log(response.body)
    }else{
        response.status = 404
        response.body = {
            success: false,
            msg: "no data input"
        }
    }
    
})

// @desc POST select song
router.post("/api/v1/select", async({request, response}: {request: any, response: any}) =>{
    if(request.hasBody){
        const body = request.body()
        const req: Req = await body.value
        console.log(req.songKey)
        const index: number | undefined = songList.findIndex(name => name.songKey === req.songKey)
        if(index !== -1){
            nowPlaying = songList[index]
            songList = songList.filter(name => name.songKey !== req.songKey)
            const sortedSongList = sortSongList(songList)
            response.status = 200
            response.body = {
                success: true,
                songlist: sortedSongList,
                nowplaying: nowPlaying
            }
        }else{
            console.log("[SEL] not found "+req.songKey)
            const sortedSongList = sortSongList(songList)
            response.status = 404
            if(nowPlaying.songName !== ""){
                response.body = {
                    success: false,
                    songlist: sortedSongList,
                    nowplaying: nowPlaying
                }
            }else{
                response.body = {
                    success: false,
                    songlist: sortedSongList
                }
            }
            
        }
    }else{
        response.status = 404
        response.body = {
            success: false,
            msg: "no data input"
        }
    }
    
})

// @desc POST delete song by songname
router.post("/api/v1/del", async({request, response}: {request: any, response: any}) =>{
    if(request.hasBody){
        const body = request.body()
        const req: Req = await body.value
        const index: number | undefined = songList.findIndex(name => name.songKey === req.songKey)
        if(index !== -1){
            songList = songList.filter(name => name.songKey !== req.songKey)
            const sortedSongList = sortSongList(songList)
            response.status = 200
            if(nowPlaying.songName !== ""){
                response.body = {
                    success: true,
                    songlist: sortedSongList,
                    nowplaying: nowPlaying
                }
            }else{
                response.body = {
                    success: true,
                    songlist: sortedSongList
                }
            }
        }else{
            console.log("[DEL] not found "+req.songKey)
            const sortedSongList = sortSongList(songList)
            response.status = 404
            if(nowPlaying.songName !== ""){
                response.body = {
                    success: false,
                    songlist: sortedSongList,
                    nowplaying: nowPlaying
                }
            }else{
                response.body = {
                    success: false,
                    songlist: sortedSongList
                }
            }
        }
    }else{
        response.status = 404
        response.body = {
            success: false,
            msg: "no data input"
        }
    }
})

// @desc POST clear song list
router.post("/api/v1/clear", async({request, response}: {request: any, response: any}) =>{
    if(request.hasBody){
        const body = request.body()
        const req: Confirm = await body.value
        if(req.confirm){
            songList = []
            nowPlaying = {
                songKey: "",
                songName: "",
                vote: 0,
                ts: new Date()
            }
            response.status = 200
            response.body = {
                success: true,
                songlist: [],
                nowplaying: nowPlaying
            }
        }
    }else{
        response.status = 404
        response.body = {
            success: false,
            msg: "no data input"
        }
    }
})

await app.listen({ port: port })
