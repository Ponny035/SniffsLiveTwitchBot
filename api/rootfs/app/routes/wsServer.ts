import { WebSocket, isWebSocketCloseEvent } from "https://deno.land/std@0.99.0/ws/mod.ts";
import { getTimestamp } from "../functions/gettimestamp.ts"
import { firstHandShake } from "../controllers/songselector.ts"

let connections = new Array;

export const handleSocket = async (ctx: any): Promise<void> =>{
    const ws: WebSocket = await ctx.upgrade()
    console.log(`[_API] [${getTimestamp()}] Websocket connection established`)
    connections.push(ws)
    for await (const event of ws){
        if(isWebSocketCloseEvent(event) || event === 'close'){
            connections = connections.filter(websocket => websocket !== ws)
            console.log(`[_API] [${getTimestamp()}] Websocket connection closed`)
        }else{
            firstHandShake()
        }
    }
}

export const socketSongList = (event: string) =>{
    for(const websocket of connections){
        if(!websocket.isClosed){
            websocket.send(event)
        }
    }
}
