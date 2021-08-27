import { WebSocket, isWebSocketCloseEvent } from "https://deno.land/std@0.99.0/ws/mod.ts";
import { getTimestamp } from "../functions/gettimestamp.ts"
import { firstHandShake } from "../controllers/songselector.ts"

let connections = new Array<{ type: string, ws: WebSocket }>();

export const handleSocket = async (ctx: any): Promise<void> =>{
    const ws: WebSocket = await ctx.upgrade()
    console.log(`[_API] [${getTimestamp()}] Websocket connection established`)
    for await (const event of ws){
        if(isWebSocketCloseEvent(event) || event === 'close'){
            connections = connections.filter(conn => conn.ws !== ws)
            console.log(`[_API] [${getTimestamp()}] Websocket connection closed`)
        }else if(event === "songfeedHandshake"){
            connections.push({ type: "songfeed", ws })
            firstHandShake()
        }else if(event === "webfeedHandshake"){
            connections.push({ type: "webfeed", ws })
        }
    }
}

export const socketSend = (type: string, event: string) =>{
    for(const conn of connections){
        if(!conn.ws.isClosed){
            if(type === conn.type){
                conn.ws.send(event)
            }
        }
    }
}
