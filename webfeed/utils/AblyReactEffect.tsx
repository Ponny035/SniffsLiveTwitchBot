import Ably from 'ably/promises'
import { useEffect } from 'react'
import type { Types } from 'ably'

const ably: Types.RealtimePromise = new Ably.Realtime.Promise({
  authUrl: '/api/createTokenRequest',
})

export const useChannel = (
  channelName: string,
  callbackonMessage: CallableFunction
): [Types.RealtimeChannelPromise, Types.RealtimePromise] => {
  const channel: Types.RealtimeChannelPromise = ably.channels.get(channelName)

  const onMount = () => {
    channel.subscribe((msg: Types.Message) => {
      callbackonMessage(msg)
    })
  }

  const onUnmount = () => {
    channel.unsubscribe()
  }

  useEffect(() => {
    onMount()
    return () => {
      onUnmount()
    }
  }, [ably])

  return [channel, ably]
}
