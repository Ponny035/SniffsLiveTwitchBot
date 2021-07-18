export const getTimestamp = (): string =>{
    const now = new Date()
    const timeString = now.toISOString().slice(0, 10)+" "+now.toISOString().slice(11, 19)
    return timeString
}
