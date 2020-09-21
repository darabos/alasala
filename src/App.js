import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from 'react-three-fiber';
import { Extrude } from 'drei';
import * as THREE from 'three';
import { Physics, useBox, usePlane, useSpring } from 'use-cannon';
import './App.css';

function Plane(props) {
  const ref = usePlane(() => ({
    material: {
      friction: 0.2,
    },
    //    rotation: [-Math.PI / 2, 0, 0]
  }));

  return (
    <mesh ref={ref}>
      <planeBufferGeometry attach="geometry" args={[10, 10]} />
      <meshStandardMaterial attach="material" color="red" />
    </mesh>
  );
}

function Box(props) {
  var current = useRef({ time: 0 }).current;
  const x = props.trajectory[0][0];
  const y = props.trajectory[0][1];
  const masterZ = -3;
  const springLength = 0.3;

  const [ref, api] = useBox(() => ({
    mass: 1,
    material: {
      friction: 0.01,
    },
    position: [x, y, 0.5],
  }));

  const [masterRef, masterApi] = useBox(() => ({
    type: 'Kinematic',
    position: [x, y, masterZ],
  }));

  useSpring(ref, masterRef, {
    restLength: springLength,
    stiffness: 12,
    damping: 2,
    localAnchorA: [0.9, 0, masterZ + springLength - 0.5],
  });

  // Set up state for the hovered and active state
  const [hovered, setHover] = useState(false);
  const [active, setActive] = useState(false);

  const lastStage = props.trajectory.length - 2;
  const stageLength = 300;

  // Rotate mesh every frame, this is outside of React without overhead
  useFrame(({ camera }) => {
    current.time += 1;
    var aX, aY;
    const stage = Math.floor(current.time / stageLength);
    if (stage > lastStage) {
      aX = props.trajectory[lastStage + 1][0];
      aY = props.trajectory[lastStage + 1][1];
    } else {
      const sX = props.trajectory[stage][0];
      const sY = props.trajectory[stage][1];
      const tX = props.trajectory[stage + 1][0];
      const tY = props.trajectory[stage + 1][1];
      const phase = (current.time % stageLength) / stageLength;
      aX = sX * (1 - phase) + tX * phase;
      aY = sY * (1 - phase) + tY * phase;
    }
    masterApi.position.set(aX, aY, masterZ);
    masterApi.velocity.set(0, 0, 0);
  });

  return (
    <mesh
      ref={ref}
      scale={active ? [1.5, 1.5, 1.5] : [1, 1, 1]}
      onClick={(e) => setActive(!active)}
      onPointerOver={(e) => setHover(true)}
      onPointerOut={(e) => setHover(false)}
    >
      <boxBufferGeometry attach="geometry" args={[1, 1, 1]} />
      <meshStandardMaterial
        attach="material"
        color={hovered ? 'hotpink' : 'orange'}
      />
    </mesh>
  );
}

function PartySelector({ data, startCombat }) {
  // TODO: let the user set the party
  const [party, setParty] = useState([
    data.heroes[0].id,
    data.heroes[0].id,
    data.heroes[0].id,
    data.heroes[0].id,
    data.heroes[0].id,
  ]);

  return (
    <div>
      {party.map((id) => {
        const h = data.heroes.find((hero) => hero.id === id);
        return <Hero hero={h} key={id} />;
      })}
      <button onClick={() => startCombat(party)}>Gooooooooooooo!</button>
    </div>
  );
}

function BattleRenderer() {
  return (
    <div style={{ height: '50vh' }}>
      <Canvas>
        <ambientLight />
        <pointLight position={[10, 10, 10]} />
        <Physics gravity={[0, 0, -10]}>
          <Plane />
          <Box
            trajectory={[
              [3, 3],
              [3, -3],
              [-3, -3],
              [-3, 3],
              [3, 3],
            ]}
          />
          <Box
            trajectory={[
              [-5, 0],
              [5, 0],
              [-5, 0],
              [5, 0],
              [-5, 0],
            ]}
          />
          <Box
            trajectory={[
              [0, -3],
              [0, 3],
              [0, -3],
              [0, 3],
              [0, -3],
            ]}
          />
        </Physics>
      </Canvas>
    </div>
  );
}

function Spinner() {
  return <div />;
}

function Combat({ data }) {
  const [state, setState] = useState('selectParty');
  const [party, setParty] = useState(null);

  function startCombat(party) {
    setParty(party);
    setState('simulate');
  }

  useEffect(() => {
    if (state === 'simulate') {
      // TODO: fetch results here
      console.log(party);
      setState('renderBattle');
    }
  }, [state]);

  return (
    <div>
      {state === 'selectParty' && (
        <PartySelector data={data} startCombat={startCombat} />
      )}
      {state === 'simulate' && <Spinner />}
      {state === 'renderBattle' && <BattleRenderer />}
    </div>
  );
}

function Map(props) {
  return (
    <div>
      <p>day {props.data.progress.day}</p>
      <p>current stage: {props.data.progress.stage}</p>
      <div style={{ height: '80vh' }}>
        <Canvas>
          <MapDiorama />
        </Canvas>
      </div>
      <p>
        <button onClick={props.searchBeach}>search the beach</button>
        <button onClick={() => props.setPage('combat')}>attack</button>
      </p>
    </div>
  );
}

function useStatic(fn) {
  const ref = useRef();
  if (!ref.current) {
    ref.current = fn();
  }
  return ref.current;
}

function MapDiorama() {
  function randomShape(r, n) {
    const s = new THREE.Shape();
    const start = r;
    s.moveTo(r, 0);
    for (let i = 1; i < n; ++i) {
      const phi = (i * Math.PI * 2) / n;
      r = (start * (9 + Math.sin(7 * phi) + Math.sin(8 * phi))) / 9;
      s.lineTo(r * Math.cos(phi), r * Math.sin(phi));
    }
    s.lineTo(start, 0);
    console.log(s);
    return s;
  }
  const shape = useStatic(() => randomShape(100, 100));
  const mesh = useRef();
  useFrame(({ camera }) => {
    camera.position.z = -200;
    camera.position.y = 100;
    camera.lookAt(0, 0, 0);
    mesh.current.rotation.z += 0.01;
    mesh.current.rotation.x = Math.PI / 2;
  });
  const extrudeSettings = useStatic(() => ({
    steps: 1,
    depth: 1,
    bevelThickness: 5,
    bevelSize: 5,
    bevelSegments: 2,
  }));
  return (
    <>
      <ambientLight />
      <pointLight position={[0, 100, 0]} />
      <Extrude
        ref={mesh}
        args={[shape, extrudeSettings]}
        position={new THREE.Vector3(0, 0, 0)}
      >
        <meshPhongMaterial attach="material" color="#691" />
      </Extrude>
    </>
  );
}

function Heroes(props) {
  return (
    <div>
      {props.data.heroes.map((h) => (
        <Hero key={h.id} hero={h}></Hero>
      ))}
    </div>
  );
}

function Hero(props) {
  return (
    <div onClick={props.onClick}>
      {props.hero.name}, level {props.hero.level}
      {props.selected && 'SELECTED'}
    </div>
  );
}

function Searched(props) {
  return (
    <div>
      <Hero hero={props.data.just_found}></Hero>
    </div>
  );
}

function App() {
  const [page, setPage] = useState('map');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    fetch('/getuserdata?user=test')
      .then((res) => res.json())
      .then(
        (res) => setData(res),
        (error) => setError(error)
      );
  }, []);
  function searchBeach() {
    fetch('/searchbeach', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user: 'test' }),
    })
      .then((res) => res.json())
      .then(
        (res) => {
          setData(res);
          setPage('searched');
        },
        (error) => setError(error)
      );
  }

  return (
    <div>
      {page}
      {error && <div>{error}</div>}
      {data && (
        <div>
          {JSON.stringify(data)}
          {page === 'combat' && <Combat data={data}></Combat>}
          {page === 'map' && (
            <Map setPage={setPage} searchBeach={searchBeach} data={data}></Map>
          )}
          {page === 'heroes' && <Heroes data={data}></Heroes>}
          {page === 'searched' && <Searched data={data}></Searched>}
        </div>
      )}
      <div>
        <button onClick={() => setPage('heroes')}>heroes</button>
        <button onClick={() => setPage('map')}>map</button>
      </div>
    </div>
  );
}

export default App;
