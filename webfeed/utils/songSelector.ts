import Ably from 'ably/promises'
import { supabase } from './supabase'
import type {
  PostgrestResponse,
  PostgrestSingleResponse,
} from '@supabase/postgrest-js'
import { Types } from 'ably'

export type Song = {
  id?: number
  songKey: string
  songName: string
  vote: number
  ts: Date
  nowPlaying: boolean
}

type VoteObj = {
  songName: string
  songVote: number
}

export type SongResponse = {
  success: boolean
  songList: Song[]
  nowPlaying?: Song
}

let songList: Song[] = []

let nowPlaying: Song = {
  id: 0,
  songKey: '',
  songName: '',
  vote: 0,
  ts: new Date(),
  nowPlaying: true,
}

let nowPlayingDef: Song = {
  id: 0,
  songKey: '',
  songName: '',
  vote: 0,
  ts: new Date(),
  nowPlaying: true,
}

const ABLY_KEY: string = process.env.ABLY_KEY || ''
const ably: Ably.Realtime = new Ably.Realtime(ABLY_KEY)
const channel: Types.RealtimeChannelPromise = ably.channels.get('songfeed')

const sortSongList = (songList: Song[]): Song[] => {
  return songList.sort((prevSong: Song, nextSong: Song): number => {
    if (prevSong.vote > nextSong.vote) return -1
    if (prevSong.vote < nextSong.vote) return 1

    if (prevSong.ts < nextSong.ts) return -1
    if (prevSong.ts > nextSong.ts) return 1
    return 0
  })
}

export const preparedResponse = async (): Promise<SongResponse> => {
  const { data: songQuery, error }: PostgrestResponse<Song> = await supabase
    .from<Song>('songrequest')
    .select('*')
  const nowPlayingIdx: number = songQuery!.findIndex(
    (i) => i.nowPlaying === true
  )
  if (nowPlayingIdx !== -1) {
    songList = songQuery!.filter((song) => song.nowPlaying === false)
    nowPlaying = songQuery![nowPlayingIdx]
  } else {
    songList = songQuery || []
    nowPlaying = nowPlayingDef
  }
  const sortedSongList = sortSongList(songList)
  let response: SongResponse = {
    success: true,
    songList: sortedSongList,
  }
  if (nowPlaying.songName !== '') {
    response = { ...response, nowPlaying }
  }
  channel.publish({ name: 'feedmessage', data: JSON.stringify(response) })
  return response
}

export const handleSongVote = async (
  votedSong: Song
): Promise<SongResponse | VoteObj> => {
  let totalVote: number = 0
  const { data: song, error }: PostgrestSingleResponse<Song> = await supabase
    .from<Song>('songrequest')
    .select('*')
    .eq('songKey', votedSong.songKey.toLowerCase())
    .single()
  if (song) {
    song.vote += votedSong.vote
    totalVote = song.vote
    await supabase
      .from<Song>('songrequest')
      .update({ vote: song.vote })
      .match({ id: song.id })
  } else {
    await supabase.from<Song>('songrequest').insert({
      songKey: votedSong.songKey.toLowerCase(),
      songName: votedSong.songName,
      vote: votedSong.vote,
      ts: new Date(votedSong.ts),
    })
    totalVote = 1
  }
  const voteObj: VoteObj = {
    songName: votedSong.songName,
    songVote: totalVote,
  }
  const songResponse = await preparedResponse()
  return { ...songResponse, ...voteObj }
}

export const setNowPlaying = async (id: number): Promise<SongResponse> => {
  const { data: songQuery, error }: PostgrestResponse<Song> = await supabase
    .from<Song>('songrequest')
    .update({ nowPlaying: true })
    .match({ id })
  if (songQuery) {
    await supabase
      .from<Song>('songrequest')
      .delete()
      .neq('id', id)
      .match({ nowPlaying: true })
  }
  return await preparedResponse()
}

export const deleteSong = async (id: number): Promise<SongResponse> => {
  await supabase.from<Song>('songrequest').delete().match({ id })
  return await preparedResponse()
}

export const clearSongList = async (
  confirm: boolean
): Promise<SongResponse> => {
  if (confirm) {
    await supabase
      .from<Song>('songrequest')
      .delete()
      .match({ nowPlaying: false })
  }
  return await preparedResponse()
}

export const removeNowPlaying = async (
  confirm: boolean
): Promise<SongResponse> => {
  if (confirm) {
    await supabase
      .from<Song>('songrequest')
      .delete()
      .match({ nowPlaying: true })
  }
  return await preparedResponse()
}
