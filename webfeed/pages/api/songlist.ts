import { preparedResponse } from '../../utils/songSelector'
import type { NextApiRequest, NextApiResponse } from 'next'

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  res.status(200).json(await preparedResponse())
}

export default handler
