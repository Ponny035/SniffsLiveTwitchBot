// declare type of Song
export interface Song {
    songKey: string,
    songName: string,
    vote: number,
    ts: Date
}

// declare type of song request
export interface Req {
    songKey: string
}

// declare type of list clear request
export interface Confirm {
    confirm: boolean
}

export interface VoteObj {
    songname: string,
    songvote: number
}
