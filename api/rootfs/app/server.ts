import { Application, Router, send } from "https://deno.land/x/oak@v7.5.0/mod.ts"
import { queryList,
         songVote,
         selectSong,
         deleteSong,
         clearList,
         removeNowPlaying } from "./songselector.ts"
import { handleSocket } from "./wsServer.ts"

const port = 8000
const app = new Application()
const router = new Router()

// Logger
app.use(async (ctx, next) =>{
    await next()
    const rt = ctx.response.headers.get("X-Response-Time")
    console.log(`[_API] [${getTimestamp()}] ${ctx.request.method} ${ctx.request.url} - ${rt}`)
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

// serve static
app.use(async(ctx) =>{
    await send(ctx, ctx.request.url.pathname, {
        root: `${Deno.cwd()}/static`,
        index: "index.html",
    })
})

// @desc GET handle WS
router.get("/ws", async (ctx: any) =>{
    const sock = await ctx.upgrade();
    handleSocket(sock);
})

// @desc GET all sorted song list
router.get("/api/v1/songlist", ({response}: {response: any}) =>{
    const res = queryList()
    response.status = res.status
    response.body = res.response
})

// @desc POST insert song / vote to song list
router.post("/api/v1/vote", async({request, response}: {request: any, response: any}) =>{
    if(request.hasBody){
        const body = request.body()
        const song: Song = await body.value
        response.body = songVote(song)
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
        const res = selectSong(req)
        response.status = res.status
        response.body = res.response
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
        const res = deleteSong(req)
        response.status = res.status
        response.body = res.response
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
        const res = clearList(req)
        response.status = res.status
        response.body = res.response
    }else{
        response.status = 404
        response.body = {
            success: false,
            msg: "no data input"
        }
    }
})

// @desc POST rem now playing
router.post("/api/v1/rem", async({request, response}: {request: any, response: any}) =>{
    if(request.hasBody){
        const body = request.body()
        const req: Confirm = await body.value
        const res = removeNowPlaying(req)
        response.status = res.status
        response.body = res.response
    }else{
        response.status = 404
        response.body = {
            success: false,
            msg: "no data input"
        }
    }
})

const getTimestamp = (): string =>{
    const now = new Date()
    const timeString = now.toISOString().slice(0, 10)+" "+now.toISOString().slice(11, 19)
    return timeString
}

await app.listen({ port: port })
