import axios from "axios";
import React, { useEffect, useState } from "react";
import { Clock, CzmlDataSource, Viewer } from "resium";

const OrbitViewer: React.FC<{}> = () => {
  const [orbits, setOrbits] = useState([]);
  useEffect(() => {
    (async () => {
      setOrbits(await (await axios.get("/api/orbits")).data);
    })();
  });

  return (
    <Viewer full>
      <Clock canAnimate shouldAnimate />
      <CzmlDataSource data={orbits}></CzmlDataSource>
    </Viewer>
  );
};

export default OrbitViewer;
