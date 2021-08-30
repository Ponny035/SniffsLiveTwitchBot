import { checkHeader } from '../../utils/checkHeader'
import { preparedResponse } from '../../utils/songSelector'
import type { NextApiRequest, NextApiResponse } from 'next'

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  if (req.headers.authorization && req.method === 'GET') {
    if (checkHeader(req.headers.authorization)) {
      res.status(200).json(await preparedResponse())
    } else {
      res.status(403).json({ success: false, msg: 'unauthorized' })
    }
  } else {
    res.status(405).json({ success: false, msg: 'method not allowed' })
  }
}

export default handler
