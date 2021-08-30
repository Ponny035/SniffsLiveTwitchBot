import Head from 'next/head'
import dynamic from 'next/dynamic'
import { NextPage } from 'next'

const WebfeedComponent: NextPage = dynamic(
  () => import('../utils/webfeedComponent'),
  {
    ssr: false,
  }
)

const Webfeed = (): JSX.Element => {
  return (
    <>
      <Head>
        <title>Sniffsbot Webfeed</title>
      </Head>
      <div className="base-container has-text-right is-size-5 mr-2">
        <WebfeedComponent />
      </div>
    </>
  )
}

export default Webfeed
