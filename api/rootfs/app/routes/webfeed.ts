import { Router } from "https://deno.land/x/oak@v7.5.0/mod.ts"
import { handleSocket } from "./wsServer.ts"

const router = new Router()

import songselectorController from "../controllers/songselector.ts"
import webfeedController from "../controllers/webfeed.ts"


router
    .get("/api/v1/songlist", songselectorController.queryList)
    .post("/api/v1/vote", songselectorController.songVote)
    .post("/api/v1/select", songselectorController.selectSong)
    .post("/api/v1/del", songselectorController.deleteSong)
    .post("/api/v1/clear", songselectorController.clearList)
    .post("/api/v1/rem", songselectorController.removeNowPlaying)
    .get("/ws", handleSocket)
    .post("/api/v1/webfeed", webfeedController.sendFeed)

export default router
