import React, {
  useCallback,
  useMemo,
  useRef,
  useState,
  useEffect,
} from 'react';
import { Canvas, useFrame } from 'react-three-fiber';
import { Plane, Extrude } from 'drei';
import WaterMaterial from './WaterMaterial.js';
import * as THREE from 'three';
import { Physics, useBox, usePlane, useSpring } from 'use-cannon';
import { EffectComposer, DepthOfField, Bloom } from 'react-postprocessing';
import './App.css';

const turnFrames = 60;
const turnMS = (1000 / 60) * turnFrames;

function BasePlane(props) {
  usePlane(() => ({
    material: {
      friction: 0.2,
    },
  }));

  return (
    <mesh>
      <planeBufferGeometry attach="geometry" args={[100, 100]} />
      <meshStandardMaterial attach="material" color="yellow" />
    </mesh>
  );
}

function Box(props) {
  var mat = useRef();
  const x = props.trajectory[0].x;
  const y = props.trajectory[0].y;
  const masterZ = -3;
  const springLength = 0.3;
  const turn = props.turn;
  const [ref] = useBox(() => ({
    mass: 1,
    material: {
      friction: 0.01,
    },
    position: [x, y, 0.5],
  }));

  const [masterRef, masterApi] = useBox(() => ({
    type: 'Static',
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

  // Rotate mesh every frame, this is outside of React without overhead
  useFrame(({ camera }) => {
    camera.position.x = 12;
    camera.position.y = 6;
    camera.position.z = 15;
    const phase = props.turnClock.phase;
    const sX = props.trajectory[turn].x;
    const sY = props.trajectory[turn].y;
    const tX = props.trajectory[turn + 1].x;
    const tY = props.trajectory[turn + 1].y;
    const aX = sX * (1 - phase) + tX * phase;
    const aY = sY * (1 - phase) + tY * phase;
    const l = (props.trajectory[turn].loyalty + 5) / 10;
    mat.current.color.r = 1 - l;
    mat.current.color.b = l;
    mat.current.color.g = 0;
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
        ref={mat}
        attach="material"
        color={hovered ? 'hotpink' : 'orange'}
      />
    </mesh>
  );
}

function PartySelector({ data, party, setParty, startCombat }) {
  function toggleHero(h) {
    // TODO: let the user set the party
    setParty(party);
  }

  return (
    <div>
      {party.map((id) => {
        const h = data.heroes.find((hero) => hero.id === id);
        return <Hero onClick={() => toggleHero(h)} hero={h} key={id} />;
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
          <BattleSimulation journal={journal} heroStories={heroStories} />
        </Physics>
      </Canvas>
    </div>
  );
}

function BattleSimulation(props) {
  const journal = props.journal;
  const heroStories = props.heroStories;

  const [turn, setTurn] = useState(0);
  var turnClock = useRef({ time: 0, turn: -1 }).current;
  useFrame(() => {
    if (turnClock.turn != turn) {
      turnClock.turn = turn;
      turnClock.time = 0;
    }
    turnClock.time += 1;
    turnClock.phase = Math.min(1, turnClock.time / turnFrames);
  });

  useEffect(() => {
    if (journal && turn < journal.length - 2) {
      const timeout = setTimeout(() => {
        setTurn(turn + 1);
      }, turnMS);
      return () => clearTimeout(timeout);
    }
  }, [turn, journal]);

  return (
    <>
      <BasePlane />
      {heroStories.map((hero) => (
        <Box
          key={hero.id}
          trajectory={hero.trajectory}
          turn={turn}
          turnClock={turnClock}
        />
      ))}
    </>
  );
}

function Spinner() {
  return <div />;
}

function Combat({ data }) {
  const [state, setState] = useState('selectParty');
  const [party, setParty] = useState([
    data.heroes[0].id,
    data.heroes[1].id,
    data.heroes[2].id,
  ]);
  const [journal, setJournal] = useState(null);

  function startCombat(party) {
    setState('simulate');
    fetch(`/computecombat?user=test&stage=${data.stage}&party=${party.join()}`)
      .then((res) => res.json())
      .then((res) => {
        setState('renderBattle');
        setJournal(res);
      });
  }

  return (
    <div>
      {state === 'selectParty' && (
        <PartySelector
          party={party}
          setParty={setParty}
          data={data}
          startCombat={startCombat}
        />
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
          <MapDiorama effects />
        </Canvas>
      </div>
      <p>
        <button onClick={props.searchBeach}>search the beach</button>
        <button onClick={() => props.setPage('combat')}>attack</button>
      </p>
    </div>
  );
}

const tmpo = new THREE.Object3D();

function MapDiorama({ effects }) {
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
  const layers = useMemo(
    () => [
      { shape: randomShape(100, 100), y: 0, color: '#691' },
      { shape: randomShape(60, 60), y: 5, color: '#562' },
      { shape: randomShape(30, 30), y: 15, color: '#999' },
    ],
    []
  );
  const extrudeSettings = useMemo(
    () => ({
      steps: 1,
      depth: 10,
      bevelThickness: 5,
      bevelSize: 5,
      bevelSegments: 2,
    }),
    []
  );

  const treeInstances = useRef();
  const trees = useMemo(
    () =>
      [
        // prettier-ignore
        { pos: [80, 5, -20], r: 20, w: 1, h: 1, count: 20, color: [[0, 0.5], [0.2, 0.7], [0, 0.2]] },
        // prettier-ignore
        { pos: [10, 5, -80], r: 18, w: 0.7, h: 1, count: 50, color: [[0.2, 0.3], [0.5, 0.7], [0, 0.2]] },
        // prettier-ignore
        { pos: [40, 5, -105], r: 10, w: 0.5, h: 0.5, count: 10, color: [[0.2, 0.3], [0.5, 0.7], [0, 0.2]] },
      ].flatMap((forest) =>
        new Array(forest.count).fill().map(() => {
          const phi = Math.random() * Math.PI * 2;
          const r = forest.r * (0.5 + Math.tan(Math.random() - 0.5));
          const w = forest.w * (1 + 4 * Math.random());
          return {
            position: [
              forest.pos[0] + Math.cos(phi) * r,
              forest.pos[1] + (w * forest.h) / forest.w,
              forest.pos[2] + Math.sin(phi) * r,
            ],
            size: [w, (w * forest.h) / forest.w, w],
            color: forest.color.map(
              (c) => c[0] + Math.random() * (c[1] - c[0])
            ),
          };
        })
      ),
    []
  );
  const treeColors = useMemo(
    () => Float32Array.from(trees.flatMap((t) => t.color)),
    [trees]
  );

  const stones = useMemo(() => {
    const p = new THREE.Vector3(41, 2, -112);
    const dir = new THREE.Vector3(-1, 0, -1);
    dir.normalize();
    dir.multiplyScalar(5);
    const up = new THREE.Vector3(0, 1, 0);
    const stones = [];
    const turns = [5, 4, 3, 4, 5, 6, 6, 5, 4, -2, -4, -8, -5, -1, 0, 0, 0, 0];
    for (let i = 0; i < turns.length; ++i) {
      stones.push({ position: p.toArray() });
      dir.applyAxisAngle(up, 0.1 * turns[i]);
      p.add(dir);
    }
    return stones;
  }, []);

  const stoneInstances = useCallback(
    (mesh) => {
      if (!mesh) return;
      for (let i = 0; i < stones.length; ++i) {
        const s = stones[i];
        tmpo.position.fromArray(s.position);
        tmpo.rotation.set(0, Math.random(), 0);
        tmpo.scale.set(1, 1, 1);
        tmpo.updateMatrix();
        mesh.setMatrixAt(i, tmpo.matrix);
      }
      mesh.instanceMatrix.needsUpdate = true;
    },
    [stones]
  );

  useFrame(({ camera, clock }) => {
    const t = clock.getElapsedTime();
    camera.position.z = -140;
    camera.position.y = 50 + 2 * Math.cos(0.19 * t);
    camera.position.x = 5 * Math.sin(0.2 * t);
    camera.lookAt(0, 0, -50);
    for (let i = 0; i < trees.length; ++i) {
      const tree = trees[i];
      const tp = tree.position;
      tmpo.position.fromArray(tp);
      tmpo.scale.fromArray(tree.size);
      tmpo.position.x +=
        0.05 *
        tree.size[0] *
        Math.sin(
          5 * t +
            0.1 * Math.cos(0.1 * t) * tp[0] +
            0.1 * Math.sin(0.1 * t) * tp[2]
        );
      tmpo.updateMatrix();
      treeInstances.current.setMatrixAt(i, tmpo.matrix);
    }
    treeInstances.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <>
      <hemisphereLight intensity={0.5} />
      <spotLight
        position={[0, 200, 0]}
        angle={1}
        penumbra={0.1}
        intensity={1.5}
        castShadow
        shadow-bias={0.000001}
        shadow-mapSize-height={1024}
        shadow-mapSize-width={1024}
      />
      <Plane
        args={[500, 500, 100, 100]}
        rotation-x={-Math.PI / 2}
        receiveShadow
      >
        <WaterMaterial />
      </Plane>
      {layers.map((l) => (
        <Extrude
          key={l.y}
          castShadow
          receiveShadow
          args={[l.shape, extrudeSettings]}
          rotation={[Math.PI / 2, 0, 4]}
          position={[0, l.y, 0]}
        >
          <meshStandardMaterial attach="material" color={l.color} />
        </Extrude>
      ))}

      <instancedMesh
        castShadow
        ref={treeInstances}
        args={[null, null, trees.length]}
      >
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

      <instancedMesh
        ref={stoneInstances}
        castShadow
        args={[null, null, stones.length]}
      >
        <boxBufferGeometry
          attach="geometry"
          args={[3, 10, 3]}
        ></boxBufferGeometry>
        <meshLambertMaterial attach="material" color="#fff" />
      </instancedMesh>

      {effects && (
        <EffectComposer>
          <DepthOfField
            focusDistance={0.1}
            focalLength={0.15}
            bokehScale={10}
            height={480}
          />
          <Bloom luminanceThreshold={0} luminanceSmoothing={0.9} height={300} />
        </EffectComposer>
      )}
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
