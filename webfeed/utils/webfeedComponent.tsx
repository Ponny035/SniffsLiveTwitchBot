import React, { useEffect, useState, useRef } from 'react'
import { useChannel } from './AblyReactEffect'
import type { NextPage } from 'next'
import type { Types } from 'ably'

type FeedMessage = {
  message: string
  to: number
}

const WebfeedComponent: NextPage = (): JSX.Element => {
  const [lastMessage, setLastMessage] = useState<FeedMessage>()
  const [receivedMessages, setReceivedMessages] = useState<FeedMessage[]>([])
  const baseRef = useRef<HTMLDivElement>(null)
  const defaultMessageTimeout = 5000

  useChannel('webfeed', (message: Types.Message) => {
    if (message.name === 'feedmessage') {
      const messageParse = JSON.parse(message.data)
      setLastMessage(messageParse)
    }
  })

  useEffect(() => {
    if (lastMessage) {
      const history = receivedMessages.slice(-199)
      setReceivedMessages([...history, lastMessage])

      const containerElement = document.createElement('div')
      containerElement.className = 'pt-2 fadein'

      const baseSpanElement = document.createElement('span')
      baseSpanElement.className = 'icon-text is-align-items-center'
      baseSpanElement.innerHTML = lastMessage.message

      containerElement.appendChild(baseSpanElement)
      baseRef.current?.appendChild(containerElement)

      setTimeout(() => {
        containerElement.classList.remove('fadein')
        containerElement.classList.add('fadeout')
        setTimeout(() => {
          baseRef.current?.removeChild(containerElement)
        }, 200)
      }, lastMessage.to | defaultMessageTimeout)
    }
  }, [lastMessage])

  return <div ref={baseRef}></div>
}

export default WebfeedComponent
