import { Application, send } from "https://deno.land/x/oak@v7.5.0/mod.ts"
import { getTimestamp } from "./functions/gettimestamp.ts"
import webfeedRouter from "./routes/webfeed.ts"

const port: number = 8000
const app = new Application()

// Logger
app.use(async(ctx: any, next) =>{
    await next()
    const rt = ctx.response.headers.get("X-Response-Time")
    console.log(`[_API] [${getTimestamp()}] ${ctx.request.method} ${ctx.request.url} - ${rt}`)
})

// Timing
app.use(async(ctx: any, next) =>{
    const start = Date.now();
    await next()
    const ms = Date.now() - start
    ctx.response.headers.set("X-Response-Time", `${ms}ms`)
    ctx.response.headers.append("Access-Control-Allow-Origin", "*")
})

app.use(webfeedRouter.routes())
app.use(webfeedRouter.allowedMethods())

// serve static
app.use(async(ctx: any, next) =>{
    await next()
    await send(ctx, ctx.request.url.pathname, {
        root: `${Deno.cwd()}/static`,
        index: "songfeed.html",
    })
})

app.addEventListener("listen", ({ secure, hostname, port }) =>{
    const protocol = secure ? "https://" : "http://"
    const url = `${protocol}${hostname ?? "localhost"}:${port}`
    console.log(`[_API] [${getTimestamp()}] Listening on : ${url}`)
})

await app.listen({ port: port })
