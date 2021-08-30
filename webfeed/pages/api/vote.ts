import { checkHeader } from '../../utils/checkHeader'
import { handleSongVote } from '../../utils/songSelector'
import type { NextApiRequest, NextApiResponse } from 'next'

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  if (req.headers.authorization && req.method === 'POST' && req.body) {
    if (checkHeader(req.headers.authorization)) {
      res.status(200).json(await handleSongVote(req.body))
    } else {
      res.status(403).json({ success: false, msg: 'unauthorized' })
    }
  } else {
    res.status(405).json({ success: false, msg: 'method not allowed' })
  }
}

export default handler
