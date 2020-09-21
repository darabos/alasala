import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from 'react-three-fiber';
import { Plane, Extrude } from 'drei';
import WaterMaterial from './WaterMaterial.js';
import * as THREE from 'three';
import { EffectComposer, DepthOfField, Bloom } from 'react-postprocessing';
import './App.css';

// Copied from example.
function Box(props) {
  // This reference will give us direct access to the mesh
  const mesh = useRef();
  var stage = useRef({ x: 0 });

  // Set up state for the hovered and active state
  const [hovered, setHover] = useState(false);
  const [active, setActive] = useState(false);

  // Rotate mesh every frame, this is outside of React without overhead
  useFrame(() => {
    if (active) {
      stage.current.x += 1;
    } else {
      stage.current.x = 0;
    }
    mesh.current.position.y = Math.abs(
      Math.sin((Math.PI * stage.current.x) / 60) * 2
    );
    mesh.current.rotation.x = mesh.current.rotation.y += 0.01;
  });

  return (
    <mesh
      {...props}
      ref={mesh}
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
    data.heroes[1].id,
    data.heroes[2].id,
    data.heroes[3].id,
    data.heroes[4].id,
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
        <Box position={[-1.2, 0, 0]} />
        <Box position={[1.2, 0, 0]} />
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
      fetch(
        `/computecombat?user=test&stage=${data.stage}&party=${party.join()}`
      )
        .then((res) => res.json())
        .then((res) => {
          console.log(res);
          setState('renderBattle');
        });
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
        <Canvas
          shadowMap
          onCreated={({ gl }) => {
            gl.setClearColor(new THREE.Color('#fff'));
          }}
        >
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
    return s;
  }
  const shape = useStatic(() => randomShape(100, 100));
  const mesh = useRef();
  useFrame(({ camera, clock }) => {
    camera.position.z = -140;
    camera.position.y = 50 + 2 * Math.cos(0.19 * clock.getElapsedTime());
    camera.position.x = 5 * Math.sin(0.2 * clock.getElapsedTime());
    camera.lookAt(0, 0, -50);
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
      <hemisphereLight intensity={0.35} />
      <spotLight
        position={[0, 200, 0]}
        angle={1}
        penumbra={1}
        intensity={2}
        castShadow
      />
      <Plane
        args={[500, 500, 100, 100]}
        rotation-x={-Math.PI / 2}
        receiveShadow
      >
        <WaterMaterial />
      </Plane>
      <Extrude
        castShadow
        receiveShadow
        ref={mesh}
        args={[shape, extrudeSettings]}
        rotation={[Math.PI / 2, 0, 4]}
      >
        <meshStandardMaterial attach="material" color="#691" />
      </Extrude>
      <EffectComposer>
        <DepthOfField
          focusDistance={0.1}
          focalLength={0.1}
          bokehScale={10}
          height={480}
        />
        <Bloom luminanceThreshold={0} luminanceSmoothing={0.9} height={300} />
      </EffectComposer>
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
