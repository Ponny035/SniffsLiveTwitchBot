const wsToken: string = process.env.WS_KEY || ''
const serverKey: string = 'jSjens73jZks73'

export const checkHeader = (token: string): boolean => {
  return token === wsToken || token === serverKey
}
