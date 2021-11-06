import type { NextPage } from "next";
import dynamic from "next/dynamic";
import React from "react";

const OrbitViewer = dynamic(() => import("../components/OrbitViewer"), {
  ssr: false,
});

const Home: NextPage = () => <OrbitViewer></OrbitViewer>;

export default Home;
