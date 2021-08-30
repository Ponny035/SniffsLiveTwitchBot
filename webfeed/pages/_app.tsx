import Head from 'next/head'
import type { AppProps } from 'next/app'
import 'bulma/bulma.sass'
import '../styles/globals.css'

const MyApp = ({ Component, pageProps }: AppProps): JSX.Element => {
  return (
    <>
      <Head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta property="og:url" content="https://songfeed.picturo.us" />
        <meta property="og:type" content="website" />
        <script
          src="https://kit.fontawesome.com/6f28d47655.js"
          crossOrigin="anonymous"
        ></script>
      </Head>
      <Component {...pageProps} />
    </>
  )
}
export default MyApp
