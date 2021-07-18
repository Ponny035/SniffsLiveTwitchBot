import { getTimestamp } from "../functions/gettimestamp.ts"
import { socketSend } from "../routes/wsServer.ts"

export default {
    sendFeed: async({ request, response }: { request: any, response: any }) =>{
        if(!request.hasBody){
            response.status = 404
            response.body = {
                success: false,
                msg: "no data input"
            }
            return
        }
        const body = request.body()
        const data = await body.value
        console.log(`[_API] [${getTimestamp()}] Webfeed sending message`)
        socketSend("webfeed", data.message)
        response.status = 200
        response.body = {
            success: true,
            msg: data.message
        }
    }
}
