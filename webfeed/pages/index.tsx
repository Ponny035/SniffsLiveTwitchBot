import Head from 'next/head'
import Link from 'next/link'
import type { NextPage } from 'next'

const Home: NextPage = (): JSX.Element => {
  return (
    <div>
      <Head>
        <title>Sniffsbot Webfeed System</title>
        <meta
          name="description"
          content="Sniffsbot Webfeed System use with Sniffs Twitch Bot"
        />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container is-flex is-flex-direction-column is-justify-content-center p-3">
        <h1 className="title has-text-weight-bold has-text-centered">
          Sniffsbot Webfeed System
        </h1>

        <div className="is-flex is-flex-direction-row">
          <Link href="/webfeed" passHref>
            <button className="button is-large has-text-weight-medium is-link mx-2 is-flex-grow-1">
              Webfeed
            </button>
          </Link>
          <Link href="/songfeed" passHref>
            <button className="button is-large has-text-weight-medium is-link mx-2 is-flex-grow-1">
              Songfeed
            </button>
          </Link>
          <Link href="/songlist" passHref>
            <button className="button is-large has-text-weight-medium is-link mx-2 is-flex-grow-1">
              Songlist Management
            </button>
          </Link>
        </div>
      </main>
    </div>
  )
}

export default Home
