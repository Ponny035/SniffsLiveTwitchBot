import { checkHeader } from '../../utils/checkHeader'
import {
  setNowPlaying,
  deleteSong,
  clearSongList,
  removeNowPlaying,
  SongResponse,
} from '../../utils/songSelector'
import type { NextApiRequest, NextApiResponse } from 'next'

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  if (req.body) {
    if (typeof req.body === 'string') {
      req.body = JSON.parse(req.body)
    }
    if (req.headers.authorization && checkHeader(req.headers.authorization)) {
      let response: SongResponse
      switch (req.method) {
        case 'POST':
          response = await setNowPlaying(req.body.id)
          if (response) {
            res.status(200).json(response)
          } else {
            res.status(404).json({ success: false, msg: 'song not found' })
          }
          break
        case 'PUT':
          response = await deleteSong(req.body.id)
          if (response) {
            res.status(200).json(response)
          } else {
            res.status(404).json({ success: false, msg: 'song not found' })
          }
          break
        case 'DELETE':
          response = await clearSongList(req.body.confirm)
          if (response) {
            res.status(200).json(response)
          } else {
            res.status(404).json({ success: false, msg: 'no confirm key' })
          }
          break
        case 'PATCH':
          response = await removeNowPlaying(req.body.confirm)
          if (response) {
            res.status(200).json(response)
          } else {
            res.status(404).json({ success: false, nsg: 'no confirm key' })
          }
          break
        default:
          res.status(405).json({ success: false, msg: 'method not allowed' })
          break
      }
    } else {
      res.status(403).json({ success: false, msg: 'unauthorized' })
    }
  } else {
    res.status(404).json({ success: false, msg: 'no data input' })
  }
}

export default handler
