import React, { useMemo, useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from 'react-three-fiber';
import { Plane, Extrude } from 'drei';
import WaterMaterial from './WaterMaterial.js';
import * as THREE from 'three';
import { Physics, useBox, usePlane, useSpring } from 'use-cannon';
import { EffectComposer, DepthOfField, Bloom } from 'react-postprocessing';
import './App.css';

function BasePlane(props) {
  const ref = usePlane(() => ({
    material: {
      friction: 0.2,
    },
  }));

  return (
    <mesh>
      <planeBufferGeometry attach="geometry" args={[100, 100]} />
      <meshStandardMaterial attach="material" color="black" />
    </mesh>
  );
}

function Box(props) {
  var current = useRef({ time: 0 }).current;
  const x = props.trajectory[0].x;
  const y = props.trajectory[0].y;
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
  const stageLength = 60;

  // Rotate mesh every frame, this is outside of React without overhead
  useFrame(({ camera }) => {
    camera.position.x = 12;
    camera.position.y = 6;
    camera.position.z = 15;
    current.time += 1;
    var aX, aY;
    const stage = Math.floor(current.time / stageLength);
    if (stage > lastStage) {
      aX = props.trajectory[lastStage + 1].x;
      aY = props.trajectory[lastStage + 1].y;
    } else {
      const sX = props.trajectory[stage].x;
      const sY = props.trajectory[stage].y;
      const tX = props.trajectory[stage + 1].x;
      const tY = props.trajectory[stage + 1].y;
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
  console.log(data);
  const [party, setParty] = useState([
    data.heroes[0].id,
    data.heroes[1].id,
    data.heroes[2].id,
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

function BattleRenderer(props) {
  const journal = props.journal;
  const heroStories = [];
  console.log('journal', journal);
  journal &&
    Object.entries(journal[0]).forEach(([id, value]) => {
      heroStories.push({
        id: id,
        trajectory: journal.map((step) => ({
          x: step[id].x * 3,
          y: step[id].y * 3,
          loyalty: step[id].loyalty,
        })),
      });
    });
  console.log('stories');
  console.log(heroStories);

  return (
    <div style={{ height: '50vh' }}>
      <Canvas>
        <ambientLight />
        <pointLight position={[10, 10, 10]} />
        <Physics gravity={[0, 0, -10]}>
          <BasePlane />
          {heroStories.map((hero) => (
            <Box key={hero.id} trajectory={hero.trajectory} />
          ))}
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
  const [journal, setJournal] = useState(null);

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
          setState('renderBattle');
          setJournal(res);
        });
    }
  }, [state]);

  return (
    <div>
      {state === 'selectParty' && (
        <PartySelector data={data} startCombat={startCombat} />
      )}
      {state === 'simulate' && <Spinner />}
      {state === 'renderBattle' && <BattleRenderer journal={journal} />}
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

const tmpo = new THREE.Object3D();

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
  const extrudeSettings = useStatic(() => ({
    steps: 1,
    depth: 1,
    bevelThickness: 5,
    bevelSize: 5,
    bevelSegments: 2,
  }));
  const treeCount = 200;
  const trees = useRef();
  const treeColors = useMemo(
    () =>
      Float32Array.from(
        new Array(treeCount)
          .fill()
          .flatMap((_, i) => [
            Math.random(),
            Math.random() * 0.5 + 0.5,
            Math.random() * 0.5,
          ])
      ),
    []
  );
  const treePositions = useMemo(() => {
    return new Array(treeCount)
      .fill()
      .map((_) => [Math.random() * 100 - 50, 10, -Math.random() * 100]);
  }, []);
  const treeSizes = useMemo(
    () => new Array(treeCount).fill().map((_) => Math.random() * 5 + 1),
    []
  );

  useFrame(({ camera, clock }) => {
    const t = clock.getElapsedTime();
    camera.position.z = -140;
    camera.position.y = 50 + 2 * Math.cos(0.19 * t);
    camera.position.x = 5 * Math.sin(0.2 * t);
    camera.lookAt(0, 0, -50);
    for (let i = 0; i < treeCount; ++i) {
      tmpo.position.fromArray(treePositions[i]);
      tmpo.rotation.z = 0.1 * Math.sin(t);
      tmpo.scale.setScalar(treeSizes[i]);
      tmpo.position.y += treeSizes[i] - 5;
      tmpo.updateMatrix();
      trees.current.setMatrixAt(i, tmpo.matrix);
    }
    trees.current.instanceMatrix.needsUpdate = true;
  });

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
      <instancedMesh castShadow ref={trees} args={[null, null, treeCount]}>
        <sphereBufferGeometry attach="geometry" args={[]}>
          <instancedBufferAttribute
            attachObject={['attributes', 'color']}
            args={[treeColors, 3]}
          />
        </sphereBufferGeometry>
        <meshLambertMaterial
          attach="material"
          vertexColors={THREE.VertexColors}
        />
      </instancedMesh>

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
