import type { AppProps } from "next/app";
import "../node_modules/cesium/Build/Cesium/Widgets/widgets.css";
import "../styles/globals.css";

function MyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}

export default MyApp;
