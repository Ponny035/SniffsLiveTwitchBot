import React, { useEffect, useState, useRef } from 'react'
import Head from 'next/head'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlayCircle } from '@fortawesome/free-solid-svg-icons'
import { useChannel } from '../utils/AblyReactEffect'
import type { NextPage } from 'next'
import type { Types } from 'ably'
import type { Song, SongResponse } from '../utils/songSelector'

// declares const class name
const containerClass = 'columns is-mobile is-size-4 text-bolder mb-3'
const listClass = 'column has-text-centered p-0'
const nameClass = 'column is-three-fifths p-0 nowrap-text'
const scoreClass = 'column has-text-centered p-0'
const linkClass = 'column has-text-centered p-0'

const serverKey: string = 'jSjens73jZks73'

const SongList: NextPage = (): JSX.Element => {
  const [songList, setSongList] = useState<Song[]>()
  const [nowPlaying, setNowPlaying] = useState<Song>()
  const songListRef = useRef<HTMLDivElement>(null)
  const nowplayingRef = useRef<HTMLDivElement>(null)
  const nameRef = useRef<HTMLDivElement[]>([])

  useChannel('songfeed', (message: Types.Message) => {
    if (message.name === 'feedmessage') {
      const messageParse: SongResponse = JSON.parse(message.data)
      setSongList(messageParse.songList)
      setNowPlaying(messageParse.nowPlaying)
    }
  })

  useEffect(() => {
    setTimeout(() => {
      fetch('/api/songlist', {
        method: 'GET',
      })
    }, 500)
  }, [])

  useEffect(() => {
    nameRef.current.forEach((element: HTMLDivElement) => {
      if (element.offsetWidth < element.scrollWidth) {
        const marquee = document.createElement('div')
        const contents = element.innerText

        marquee.innerText = contents
        marquee.className = 'sliding-text'
        element.innerHTML = ''
        element.appendChild(marquee)
      }
    })
  }, [songList, nowPlaying])

  const selectSong = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    const id: number = parseInt(e.currentTarget.id)
    fetch('/api/songmanage', {
      method: 'POST',
      headers: new Headers({ Authorization: serverKey }),
      body: JSON.stringify({ id }),
    })
  }

  const deleteSong = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    const id: number = parseInt(e.currentTarget.id)
    fetch('/api/songmanage', {
      method: 'PUT',
      headers: new Headers({ Authorization: serverKey }),
      body: JSON.stringify({ id }),
    })
  }

  const remNowPlaying = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    fetch('/api/songmanage', {
      method: 'PATCH',
      headers: new Headers({ Authorization: serverKey }),
      body: JSON.stringify({ confirm: true }),
    })
  }

  return (
    <>
      <Head>
        <title>Sniffsbot Songfeed</title>
      </Head>
      <div className="songfeed is-flex is-flex-direction-column">
        <div ref={songListRef} className="is-flex is-flex-direction-column">
          <p className="has-text-centered is-underlined is-size-3 text-bolder mb-4">
            Song List
          </p>
          {songList &&
            songList.map((song: Song, index: number) => {
              return (
                <div key={`container_${index}`} className={containerClass}>
                  <div key={`list_${index}`} className={listClass}>
                    [{(index + 1).toString()}]
                  </div>
                  <div
                    key={`name_${index}`}
                    className={nameClass}
                    ref={(div) => div && nameRef.current.push(div)}
                  >
                    {song.songName}
                  </div>
                  <div key={`score_${index}`} className={scoreClass}>
                    {song.vote.toString()} pts
                  </div>
                  <div className={linkClass}>
                    <button
                      id={song.id?.toString()}
                      className="button is-primary m-1"
                      onClick={selectSong}
                    >
                      Select
                    </button>
                  </div>
                  <div className={linkClass}>
                    <button
                      id={song.id?.toString()}
                      className="button is-primary m-1"
                      onClick={deleteSong}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )
            })}
        </div>
        <div ref={nowplayingRef} className="is-flex is-flex-direction-column">
          <p className="has-text-centered is-underlined is-size-3 text-bolder mb-4">
            Now Playing
          </p>
          {nowPlaying && (
            <div className={containerClass}>
              <div className={listClass}>
                <span className="icon">
                  <FontAwesomeIcon icon={faPlayCircle} />
                </span>
              </div>
              <div
                className={nameClass}
                ref={(div) => div && nameRef.current.push(div)}
              >
                {nowPlaying.songName}
              </div>
              <div className={scoreClass}>{nowPlaying.vote} pts</div>
              <div className={linkClass}>
                <button
                  className="button is-primary m-1"
                  onClick={remNowPlaying}
                >
                  Delete
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default SongList
