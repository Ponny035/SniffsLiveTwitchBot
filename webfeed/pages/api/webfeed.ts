import Ably from 'ably/promises'
import { checkHeader } from '../../utils/checkHeader'
import type { NextApiRequest, NextApiResponse } from 'next'
import type { Types } from 'ably'

const ABLY_KEY: string = process.env.ABLY_KEY || ''
const ably: Ably.Realtime = new Ably.Realtime(ABLY_KEY)
const channel: Types.RealtimeChannelPromise = ably.channels.get('webfeed')

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  if (req.headers.authorization && req.body && req.method === 'POST') {
    if (checkHeader(req.headers.authorization)) {
      channel.publish({ name: 'feedmessage', data: JSON.stringify(req.body) })
      res
        .status(200)
        .json({ success: true, msg: req.body.message, to: req.body.to })
    } else {
      res.status(403).json({ success: false, msg: 'unauthorized' })
    }
  } else {
    res.status(404).json({ success: false, msg: 'no data input' })
  }
}

export default handler
