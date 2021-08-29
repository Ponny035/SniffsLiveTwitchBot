import Ably from 'ably/promises'
import { NextApiRequest, NextApiResponse } from 'next'
import type { Types } from 'ably'

const ABLY_KEY: string = process.env.ABLY_KEY || ''

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  const client: Ably.Realtime = new Ably.Realtime(ABLY_KEY)
  const tokenRequestData: Types.TokenRequest =
    await client.auth.createTokenRequest({ clientId: 'sniffs-webfeed' })
  res.status(200).json(tokenRequestData)
}

export default handler
