const wsToken = process.env.WS_KEY

export const checkHeader = (token: string): boolean => {
  return token === wsToken
}
