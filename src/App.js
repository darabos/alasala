import React, {
  createRef,
  useCallback,
  useMemo,
  useRef,
  useState,
  useEffect,
} from 'react';
import { useSpring as useReactSpring, animated } from 'react-spring';
import { Canvas, useFrame } from 'react-three-fiber';
import { Plane, Extrude } from 'drei';
import WaterMaterial from './WaterMaterial.js';
import * as THREE from 'three';
import { Physics, useBox, usePlane, useSpring } from 'use-cannon';
import { EffectComposer, DepthOfField, Bloom } from 'react-postprocessing';
import './App.css';
import '@openfonts/grenze-gotisch_latin';
import '@openfonts/corben_latin';

const turnFrames = 60;

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

const HeroBox = React.forwardRef((props, ref) => {
  var mat = useRef();
  const x = props.trajectory[0].x;
  const y = props.trajectory[0].y;
  const masterZ = -3;
  const springLength = 0.3;
  const turn = props.turn;
  const [, api] = useBox(
    () => ({
      mass: 1,
      material: {
        friction: 0.01,
      },
      position: [x, y, 0.5],
    }),
    ref
  );

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
  useFrame(() => {
    ref.current.physicsApi = api;
    const phase = props.turnClock.phase;
    const sX = props.trajectory[turn].x;
    const sY = props.trajectory[turn].y;
    const tX = props.trajectory[turn + 1].x;
    const tY = props.trajectory[turn + 1].y;
    const aX = sX * (1 - phase) + tX * phase;
    const aY = sY * (1 - phase) + tY * phase;
    const l = props.trajectory[turn].loyalty;
    const scaled = (l + Math.sign(l) * 2 + 7) / 14;
    mat.current.color.r = 1 - scaled;
    mat.current.color.b = scaled;
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
});

function SimpleAttack(props) {
  //const [ref, api] = useSphere(() => ({type: 'Static', radius: 0.2}));
  const mesh = useRef();
  const sourceHero = props.sourceHero.current;
  const targetHero = props.targetHero.current;
  useFrame(() => {
    const phase = props.turnClock.phase;
    const sX = sourceHero.position.x;
    const sY = sourceHero.position.y;
    const tX = targetHero.position.x;
    const tY = targetHero.position.y;
    const aX = sX * (1 - phase) + tX * phase;
    const aY = sY * (1 - phase) + tY * phase;
    mesh.current && mesh.current.position.set(aX, aY, 2);
    if (props.turnClock.time === turnFrames && props.attackTurn === 0) {
      const force = new THREE.Vector3(tX - sX, tY - sY, 0);
      force.normalize().multiplyScalar(25);
      const localForce = targetHero.worldToLocal(force);
      targetHero.physicsApi.applyLocalForce(localForce.toArray(), [0, 0, 1]);
    }
  });
  return (
    <mesh ref={mesh}>
      <sphereBufferGeometry attach="geometry" args={[0.2, 32, 32]} />
      <meshStandardMaterial attach="material" color="black" />
    </mesh>
  );
}
function renderAction(
  heroRef,
  actionHeroId,
  actionTurn,
  turn,
  turnClock,
  action,
  key
) {
  const attackTurn = turn - actionTurn;
  const defaultProps = {
    sourceHero: heroRef(actionHeroId),
    attackTurn: attackTurn,
    turnClock: turnClock,
    key: key,
    action: action,
  };
  if (action.name === 'base_attack' && attackTurn >= -1 && attackTurn <= 0) {
    return (
      <SimpleAttack
        targetHero={heroRef(action.target_hero)}
        {...defaultProps}
      />
    );
  }
}

function PartySelector({ data, party, setParty, startCombat }) {
  function removeHero(i) {
        const p = [...party];
        p[i] = undefined;
    setParty(p);
  }
  function addHero(h) {
      const s = party.indexOf(undefined);
      if (s !== -1) {
        const p = [...party];
        p[s] = h.id;
        setParty(p);
      }
  }

  return <>
    <div className="Party">
      {party.map((id, i) => {
        const h = data.heroes.find((hero) => hero.id === id);
        if (h === undefined) {
          return <div key={i} className="CardBack"/>
        } else {
          return <HeroListItem key={i} onClick={() => removeHero(i)} hero={h} />;
        }
      })}
    </div>
    <p className="Hint Center">{party.length} heroes can join this fight. Choose them from your roster below.</p>
      <button disabled={party.filter(h => h === undefined).length === party.length} onClick={() => startCombat(party)}>Fight!</button>
    <HeroList heroes={data.heroes.filter(h => !party.includes(h.id))} onClick={h => addHero(h)}/>
  </>;
}

function BattleRenderer(props) {
  const journal = props.journal;
  const heroStories = [];
  const actionEntries = [];
  console.log('journal', journal);
  if (journal) {
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
    for (let turn = 0; turn < journal.length; turn++) {
      const turnData = journal[turn];
      Object.entries(turnData).forEach(([heroId, { actions }]) => {
        actions.forEach((action) => {
          actionEntries.push({
            action: action,
            actionHeroId: parseInt(heroId),
            actionTurn: turn,
            actionKey: 'action' + actionEntries.length,
          });
        });
      });
    }
  }
  console.log('stories');
  console.log(heroStories);
  console.log('actions');
  console.log(actionEntries);

  return (
    <div style={{ height: '50vh' }}>
      <Canvas>
        <ambientLight />
        <pointLight position={[10, 10, 10]} />
        <Physics gravity={[0, 0, -10]}>
          <BattleSimulation
            journal={journal}
            heroStories={heroStories}
            actionEntries={actionEntries}
          />
        </Physics>
      </Canvas>
    </div>
  );
}

function BattleSimulation(props) {
  const journal = props.journal;
  const heroStories = props.heroStories;
  const actionEntries = props.actionEntries;
  const heroRefs = useRef({}).current;
  function heroRef(id) {
    return heroRefs[id] || (heroRefs[id] = createRef());
  }

  const [turn, setTurn] = useState(0);
  const turnClock = useRef({ time: 0, turn: -1 }).current;
  useFrame(({ camera }) => {
    if (journal) {
      camera.position.x = 12;
      camera.position.y = 6;
      camera.position.z = 15;
      if (turnClock.turn !== turn) {
        turnClock.turn = turn;
        turnClock.time = 0;
      }
      turnClock.time += 1;
      turnClock.phase = Math.min(1, turnClock.time / turnFrames);
      if (turnClock.time === turnFrames) {
        if (journal && turn < journal.length - 2) {
          setTurn(turn + 1);
        }
      }
    }
  });
  return (
    <>
      <BasePlane />
      {heroStories.map((hero) => (
        <HeroBox
          key={hero.id}
          ref={heroRef(hero.id)}
          trajectory={hero.trajectory}
          turn={turn}
          turnClock={turnClock}
        />
      ))}
      {actionEntries.map((entry) => {
        return renderAction(
          heroRef,
          entry.actionHeroId,
          entry.actionTurn,
          turn,
          turnClock,
          entry.action,
          entry.actionKey
        );
      })}
    </>
  );
}

function Spinner() {
  return <div />;
}

function Combat({ data }) {
  const [state, setState] = useState('selectParty');
  const [party, setParty] = useState(new Array(5).fill());
  const [journal, setJournal] = useState(null);
  useEffect(() => window.scrollTo(0, 0), []);

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
  useEffect(() => window.scrollTo(0, 0), []);
  return (
    <div>
      <p>day {props.data.progress.day}</p>
      <p>current stage: {props.data.progress.stage}</p>
      <div className="MapCanvas">
        <Canvas
          shadowMap
          gl={{ antialias: false, alpha: false }}
          onCreated={({ gl }) => {
            gl.setClearColor(new THREE.Color('#fff'));
          }}
        >
          <MapDiorama effects />
        </Canvas>
      </div>
      <p>
        <button onClick={props.searchBeach}>Search the beach</button>
        <button onClick={() => props.setPage('combat')}>Next stage</button>
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

  const stoneInstances = useRef();
  const setStoneInstances = useCallback(
    (mesh) => {
      if (!mesh) return;
      for (let i = 0; i < stones.length; ++i) {
        const s = stones[i];
        tmpo.position.fromArray(s.position);
        tmpo.rotation.set(0, Math.random(), 0);
        tmpo.scale.set(1, 1, 1);
        tmpo.updateMatrix();
        mesh.setMatrixAt(i, tmpo.matrix);
        mesh.setColorAt(i, new THREE.Color('#fff'));
      }
      mesh.instanceMatrix.needsUpdate = true;
      stoneInstances.current = mesh;
    },
    [stones]
  );
  function colorStone(i, c) {
    const mesh = stoneInstances.current;
    mesh.setColorAt(i, new THREE.Color(c));
    mesh.instanceColor.needsUpdate = true;
  }

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
        ref={setStoneInstances}
        castShadow
        args={[null, null, stones.length]}
        onPointerMove={(e) => colorStone(e.instanceId, '#f00')}
        onPointerOut={(e) => colorStone(e.instanceId, '#fff')}
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

function HeroList(props) {
  return (
    <div className="HeroList">
      {props.heroes.map((h) => (
        <HeroListItem
          key={h.id}
          hero={h}
          showLevel
          onClick={() => props.onClick(h)}
        />
      ))}
    </div>
  );
}
function heroPortrait(hero) {
  return (
    'url(/portraits/' + hero.name.toLowerCase().replace(' ', '-') + '.png)'
  );
}

function HeroListItem({ showLevel, hero, onClick }) {
  return (
    <>
      <div className="HeroCard Clickable" onClick={onClick}>
        <div className="CardBackground" />
        <div
          className="CardPortrait"
          style={{ backgroundImage: heroPortrait(hero) }}
        />
        <div className="CardName"> {hero.name} </div>
        {showLevel && <div className="CardLevel"> {hero.level} </div>}
      </div>
    </>
  );
}

function HeroCard({ hero }) {
  const config = { tension: 100 };
  const [reveal, setReveal] = useState(false);
  const flip = useReactSpring({
    config,
    transform: `rotate3d(0, 1, 0, ${reveal ? 0 : 180}deg)`,
    from: { transform: 'rotate3d(0, 1, 0, 180deg)' },
  });
  const backflip = useReactSpring({
    config,
    transform: `rotate3d(0, 1, 0, ${reveal ? 180 : 360}deg)`,
    from: { transform: 'rotate3d(0, 1, 0, 360deg)' },
  });
  return (
    <>
      <animated.div
        style={backflip}
        className="CardBack Clickable"
        onClick={() => setReveal(true)}
      />
      <animated.div style={flip} className="HeroCard">
        <div className="CardBackground" />
        <div
          className="CardPortrait"
          style={{ backgroundImage: heroPortrait(hero) }}
        />
        <div className="CardName"> {hero.name} </div>
      </animated.div>
    </>
  );
}

function HeroPage({ hero }) {
  hero.name = 'Professor Hark';
  hero.title = 'Dean of Arcane Studies';
  hero.abilities = [
    {
      name: 'Bookstorm',
      description:
        'Hark throws 5 books at opponents ahead of him.  Unlocked at level 1.',
      unlocked: true,
    },
    {
      name: 'Scientific Method',
      description:
        'Hark damages everyone around him 5 times and observes the results.  Unlocked at level 5.',
      unlocked: false,
    },
    {
      name: 'Reading Glasses',
      description: 'Passive. Hark never misses. Unlocked at level 10.',
      unlocked: false,
    },
  ];
  return (
    <div className="HeroPage">
      <div
        className="HeroPortrait"
        style={{ backgroundImage: heroPortrait(hero) }}
      />
      <div className="HeroText">
        <div className="HeroName"> {hero.name} </div>
        <div className="HeroTitle">
          {' '}
          Level {hero.level} {hero.title}{' '}
        </div>
        <div className="HeroAbilities">
          <div className="PanelHeader">Abilities:</div>
          {hero.abilities.map((a) => (
            <div
              key={a.name}
              className={'HeroAbility ' + (a.unlocked ? 'Unlocked' : 'Locked')}
            >
              <h1>{a.name}</h1>
              <p>{a.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Searched(props) {
  useEffect(() => window.scrollTo(0, 0), []);
  props.data.just_found = { name: 'Professor Hark' };
  return (
    <div className="Searched">
      <HeroCard hero={props.data.just_found}></HeroCard>
    </div>
  );
}

function App() {
  const [page, setPage] = useState('map');
  const [heroPage, setHeroPage] = useState();
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
          {page === 'combat' && <Combat data={data} />}
          {page === 'map' && (
            <Map setPage={setPage} searchBeach={searchBeach} data={data} />
          )}
          {page === 'heroes' && (
            <HeroList
              heroes={data.heroes}
              onClick={(h) => {
                setPage('hero');
                setHeroPage(h);
              }}
            />
          )}
          {page === 'hero' && <HeroPage hero={heroPage} />}
          {page === 'searched' && <Searched data={data} />}
        </div>
      )}
      <div>
        <button onClick={() => setPage('heroes')}>Heroes</button>
        <button onClick={() => setPage('map')}>Map</button>
      </div>
    </div>
  );
}

export default App;
