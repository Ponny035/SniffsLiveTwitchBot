import { WebSocket, isWebSocketCloseEvent } from "https://deno.land/std@0.99.0/ws/mod.ts";
import { preparedResponse } from "./songselector.ts"

let connections = new Array;

export const handleSocket = async (ws: WebSocket): Promise<void> =>{
    console.log(`[_API] [${getTimestamp()}] Websocket connection established`)
    connections.push(ws)
    for await (const event of ws){
        if(isWebSocketCloseEvent(event) || event === 'close'){
            connections = connections.filter(websocket => websocket !== ws)
            console.log(`[_API] [${getTimestamp()}] Websocket connection closed`)
        }else{
            preparedResponse()
        }
    }
}

export const broadcastEvents = (event: string) =>{
    for(const websocket of connections){
        if(!websocket.isClosed){
            websocket.send(event)
        }
    }
}

const getTimestamp = (): string =>{
    const now = new Date()
    const timeString = now.toISOString().slice(0, 10)+" "+now.toISOString().slice(11, 19)
    return timeString
}
