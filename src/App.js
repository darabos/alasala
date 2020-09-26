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
import { Plane, Extrude, Html, Box } from 'drei';
import WaterMaterial from './WaterMaterial.js';
import * as THREE from 'three';
import {
  Physics,
  useBox,
  usePlane,
  useSpring,
  useConeTwistConstraint,
} from 'use-cannon';
import { EffectComposer, DepthOfField, Bloom } from 'react-postprocessing';
import './App.css';
import '@openfonts/grenze-gotisch_latin';
import '@openfonts/corben_latin';
import { Howl, Howler } from 'howler';

const turnFrames = 20;

function BasePlane(props) {
  usePlane(() => ({
    material: {
      friction: 0.2,
    },
  }));

  return (
    <Plane args={[200, 200]} receiveShadow>
      <meshStandardMaterial attach="material" color="#691" />
    </Plane>
  );
}

const HeroBox = React.forwardRef((props, heroRef) => {
  const meta = props.meta;
  const weight = meta.weight;
  const keelZ = -3;
  const turn = props.turn;
  const initial = props.trajectory[0];
  const height = meta.shape.size[2];
  const current = props.trajectory[turn];
  const last = props.trajectory[turn - 1] || current;
  const next = props.trajectory[turn + 1] || current;

  const [leashRef, leashApi] = useBox(() => ({
    collisionFilterMask: 0,
    type: 'Static',
    position: [initial.x, initial.y, height / 2],
  }));
  const [keelRef, keelApi] = useBox(() => ({
    collisionFilterMask: 0,
    type: 'Static',
    position: [initial.x, initial.y, keelZ],
  }));

  useSpring(heroRef, leashRef, {
    restLength: 0,
    stiffness: 12 * weight,
    damping: 2,
    localAnchorA: [0, props.leashPos || -0.9, 0],
  });
  useSpring(heroRef, keelRef, {
    restLength: 0,
    stiffness: 3 * weight,
    damping: 0,
    localAnchorA: [0, 0, -height / 2 - 2],
  });

  useFrame(() => {
    if (!heroRef.current) return;
    const phase = props.turnClock.phase;
    const aX = current.x * (1 - phase) + next.x * phase;
    const aY = current.y * (1 - phase) + next.y * phase;
    leashApi.position.set(aX, aY, height / 2);
    leashApi.velocity.set(0, 0, 0);
    keelApi.position.set(
      heroRef.current.position.x,
      heroRef.current.position.y,
      keelZ
    );
    keelApi.velocity.set(0, 0, 0);
  });
  if (last.status.find((s) => s.type === 'Removed')) {
    return;
  }
  const textLabels = current.status
    .map((s) => s.type)
    .concat(current.actions.map((a) => a.animation_name))
    .join(', ');

  return (
    <HeroBodyPart
      shape={meta.shape}
      ref={heroRef}
      position={[initial.x, initial.y]}
    >
      {'loyalty' in current ? (
        <Html center position-z={2}>
          <LoyaltyBar
            max={current.max_loyalty || Math.abs(initial.loyalty)}
            current={current.loyalty}
            change={current.loyalty - last.loyalty}
          />
          <InspirationBar value={current.inspiration} />
          <div className="CombatLabels">{textLabels}</div>
        </Html>
      ) : undefined}
    </HeroBodyPart>
  );
});

function LoyaltyBar({ max, current, change }) {
  let baseClass = 'LoyaltyBar';
  let changeClass = 'LoyaltyBarChange';
  if (current < 0) {
    current *= -1;
    change *= -1;
    baseClass += ' Evil';
  }
  let base = (current * 100) / max;
  change *= 100 / max;
  if (change < 0) {
    changeClass += ' Damage';
    change *= -1;
  } else {
    changeClass += ' Heal';
    base -= change;
  }
  return (
    <div className={baseClass}>
      <div className="LoyaltyBarInside" style={{ width: base + '%' }} />
      <div className={changeClass} style={{ width: change + '%' }} />
    </div>
  );
}

function InspirationBar({ value }) {
  return (
    <div className="InspirationBar">
      {new Array(value).fill().map((_, i) => (
        <div key={i} className="InspirationMark" />
      ))}
    </div>
  );
}

function SimpleAttack(props) {
  const mesh = useRef();
  const damage = props.damage;
  const color = props.color || 'black';
  useFrame(() => {
    const sourceHero = props.sourceHero.current;
    const targetHero = props.targetHero.current;
    if (!sourceHero || !targetHero) {
      return;
    }
    const phase = (props.turnClock.phase + props.attackTurn + 1) / 2;
    const src = sourceHero.position;
    const dst = targetHero.position;
    mesh.current && mesh.current.position.lerpVectors(src, dst, phase);
    if (props.turnClock.time === turnFrames && props.attackTurn === 0) {
      const force = dst
        .clone()
        .sub(src)
        .normalize()
        .multiplyScalar(5 * damage);
      const localForce = targetHero.worldToLocal(force);
      targetHero.physicsApi.applyLocalImpulse(localForce.toArray(), [0, 0, 1]);
    }
  });
  const radius = Math.pow(damage, 1 / 3) * 0.2;
  return (
    <mesh ref={mesh}>
      <sphereBufferGeometry attach="geometry" args={[radius, 32, 32]} />
      <meshStandardMaterial attach="material" color={color} />
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
  if (
    action.animation_name === 'Attack' &&
    attackTurn >= -1 &&
    attackTurn <= 0
  ) {
    return (
      <SimpleAttack
        targetHero={heroRef(action.target_hero)}
        damage={action.damage}
        {...defaultProps}
      />
    );
  }
  if (
    action.animation_name === 'Channeling' &&
    attackTurn >= -1 &&
    attackTurn <= 0
  ) {
    return (
      <>
        <SimpleAttack
          targetHero={heroRef(action.target_hero)}
          damage={action.damage}
          {...defaultProps}
        />
        <SimpleAttack
          targetHero={heroRef(action.beneficiary_hero)}
          damage={action.damage}
          color="white"
          {...defaultProps}
        />
      </>
    );
  }
}

function PartySelector({ data, party, setParty, startCombat }) {
  const partyNames = party
    .filter((id) => id !== null)
    .map((id) => data.heroes.find((h) => h.id === id).name);
  function removeHero(i) {
    const p = [...party];
    p[i] = null;
    setParty(p);
  }
  function addHero(h) {
    const s = party.indexOf(null);
    if (s !== -1) {
      const p = [...party];
      p[s] = h.id;
      setParty(p);
    }
  }

  return (
    <>
      <div className="Party">
        {party.map((id, i) => {
          const h = data.heroes.find((hero) => hero.id === id);
          if (h === undefined) {
            return <div key={i} className="CardBack" />;
          } else {
            return (
              <HeroListItem key={i} onClick={() => removeHero(i)} hero={h} />
            );
          }
        })}
      </div>
      <p className="Hint Center">
        {party.length} heroes can join this fight. Choose them from your roster
        below. You can only use one copy of each hero.
      </p>
      <button
        disabled={party.filter((h) => h === null).length === party.length}
        onClick={() => startCombat(party)}
      >
        Fight!
      </button>
      <HeroList
        heroes={data.heroes.filter((h) => !partyNames.includes(h.name))}
        onClick={(h) => addHero(h)}
      />
    </>
  );
}

function BattleRenderer(props) {
  const data = props.data;
  const journal = props.journal;
  const result =
    props.winner === 1 ? 'Victory!' : props.winner === 0 ? 'Draw!' : 'Defeat!';
  const [battleIsOver, setBattleIsOver] = useState(false);
  const [replayId, setReplayId] = useState(0);
  const heroStories = [];
  const actionEntries = [];
  console.log('journal', journal);
  if (journal) {
    Object.entries(journal[0]).forEach(([id, value]) => {
      const meta = data.index[value.name];
      heroStories.push({
        id: id,
        meta: meta,
        trajectory: journal.map((step) => ({
          ...step[id],
          x: step[id].x * 3,
          y: step[id].y * 3,
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

  function restartBattle() {
    setReplayId(replayId + 1);
    setBattleIsOver(false);
    props.setShowButtons(false);
  }

  return (
    <div className="CombatCanvas">
      {battleIsOver && (
        <div className="overlay">
          <div id="result">{result}</div>
          <button onClick={restartBattle}>Replay</button>
        </div>
      )}

      <CombatCanvas
        key={'combat-canvas-' + replayId}
        effects={props.effects}
        lightPosition={[20, 0, 5]}
      >
        <BattleSimulation
          journal={journal}
          heroStories={heroStories}
          actionEntries={actionEntries}
          battleOverCallback={() => {
            setBattleIsOver(true);
            props.setShowButtons(true);
          }}
        />
      </CombatCanvas>
    </div>
  );
}

function CombatCanvas({ effects, lightPosition, children }) {
  return (
    <Canvas shadowMap>
      {effects && (
        <EffectComposer>
          <Bloom luminanceThreshold={0} luminanceSmoothing={0.9} height={300} />
        </EffectComposer>
      )}
      <spotLight
        position={[-3, 0, 1]}
        color={0x9999ff}
        angle={1}
        penumbra={0.1}
        intensity={0.5}
        castShadow
        shadow-mapSize-height={1024}
        shadow-mapSize-width={1024}
      />
      <spotLight
        position={lightPosition}
        angle={0.5}
        penumbra={0.1}
        intensity={1.0}
        castShadow
        shadow-mapSize-height={1024}
        shadow-mapSize-width={1024}
      />
      <ambientLight args={[0x808080]} />
      <Physics gravity={[0, 0, -10]}>{children}</Physics>
    </Canvas>
  );
}

function BattleSimulation({
  journal,
  heroStories,
  actionEntries,
  battleOverCallback,
}) {
  const heroRefs = useRef({}).current;
  function heroRef(id) {
    return heroRefs[id] || (heroRefs[id] = createRef());
  }
  function findMidpoint() {
    const min = new THREE.Vector3();
    const max = new THREE.Vector3();
    for (const h of heroStories) {
      const c = heroRef(h.id).current;
      if (c) {
        min.min(c.position);
        max.max(c.position);
      }
    }
    return min.lerp(max, 0.5);
  }

  const [turn, setTurn] = useState(0);
  const turnClock = useRef({ time: 0, turn: -1, midpoint: new THREE.Vector3() })
    .current;

  useFrame(({ camera, clock }) => {
    if (journal) {
      const t = clock.getElapsedTime();
      camera.up.set(0, 0, 1);
      camera.fov = 40;
      camera.updateProjectionMatrix();
      camera.position.x = 3 * Math.cos(0.19 * t);
      camera.position.y = 3 * Math.sin(0.2 * t) - 40;
      camera.position.z = 15;
      turnClock.midpoint.lerp(findMidpoint(), 0.1);
      camera.lookAt(turnClock.midpoint);
      if (turnClock.turn !== turn) {
        turnClock.turn = turn;
        turnClock.time = 0;
      }
      turnClock.time += 1;
      turnClock.phase = Math.min(1, turnClock.time / turnFrames);
      if (turnClock.time === turnFrames) {
        if (journal && turn < journal.length - 1) {
          setTurn(turn + 1);
        } else {
          battleOverCallback();
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
          meta={hero.meta}
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

function lastParty(data) {
  const j = JSON.parse(localStorage.getItem('last party'));
  const p = j || new Array(5).fill().map(() => null);
  return p.map(id => data.heroes.find(h => h.id === id) ? id : null);
}

function Combat({ data, setShowButtons }) {
  const [state, setState] = useState('selectParty');
  const [party, setParty] = useState(lastParty(data));
  localStorage.setItem('last party', JSON.stringify(party));
  const [journal, setJournal] = useState();
  const [winner, setWinner] = useState();
  useEffect(() => window.scrollTo(0, 0), []);

  function startCombat(party) {
    setState('simulate');
    console.log('Starting battle with party: ', party);
    post('/computecombat', {
      user: 'test',
      stage: data.progress.stage,
      party: party,
    })
      .then((res) => res.json())
      .then((res) => {
        setState('renderBattle');
        setShowButtons(false);
        setJournal(res.log);
        setWinner(res.winner);
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
      {state === 'renderBattle' && (
        <BattleRenderer
          effects
          journal={journal}
          winner={winner}
          data={data}
          setShowButtons={setShowButtons}
        />
      )}
    </div>
  );
}

function Map(props) {
  useEffect(() => window.scrollTo(0, 0), []);
  return (
    <div>
      <div className="MapCanvas">
        <Canvas
          shadowMap
          gl={{ antialias: false, alpha: false }}
          onCreated={({ gl }) => {
            gl.setClearColor(new THREE.Color('#fff'));
          }}
        >
          <MapDiorama effects stage={props.data.progress.stage} />
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

function MapDiorama({ effects, stage }) {
  function randomShape(fn, n) {
    const s = new THREE.Shape();
    s.moveTo(fn(0), 0);
    for (let i = 1; i < n; ++i) {
      const phi = (i * Math.PI * 2) / n;
      const r = fn(phi);
      s.lineTo(r * Math.cos(phi), r * Math.sin(phi));
    }
    s.lineTo(fn(0), 0);
    return s;
  }
  const layers = useMemo(
    () =>
      [
        // prettier-ignore
        { fn: phi => (100 * (9 + Math.sin(7 * phi) + Math.sin(8 * phi))) / 9, segments: 100, y: 0, color: '#691' },
        // prettier-ignore
        { fn: phi => (60 * (9 + Math.sin(7 * phi) + Math.sin(8 * phi))) / 9, segments: 60, y: 5, color: '#562' },
        // prettier-ignore
        { fn: phi => (30 * (9 + Math.sin(7 * phi) + Math.sin(8 * phi))) / 9, segments: 30, y: 15, color: '#999' },
      ].map((e) => {
        e.shape = randomShape(e.fn, e.segments);
        return e;
      }),
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
        { pos: [80, -20], r: 20, w: 1, h: 1, count: 50, color: [[0, 0.5], [0.2, 0.7], [0, 0.2]] },
        // prettier-ignore
        { pos: [10, -80], r: 18, w: 0.7, h: 1, count: 50, color: [[0.2, 0.3], [0.5, 0.7], [0, 0.2]] },
        // prettier-ignore
        { pos: [40, -105], r: 10, w: 0.5, h: 0.5, count: 10, color: [[0.2, 0.3], [0.5, 0.7], [0, 0.2]] },
        // prettier-ignore
        { pos: [-80, -20], r: 50, w: 1, h: 1, count: 50, color: [[0.5, 0.8], [0.2, 0.7], [0, 0.2]] },
        // prettier-ignore
        { pos: [0, 0], r: 200, w: 0.4, h: 0.3, count: 2000, color: [[0, 0.5], [0.2, 0.7], [0, 0.2]] },
      ].flatMap((forest) =>
        new Array(forest.count).fill().map(() => {
          while (true) {
            const phi = Math.random() * Math.PI * 2;
            const r = forest.r * Math.sqrt(Math.random());
            const w = forest.w * (1 + 4 * Math.random());
            const h = w * (forest.h / forest.w);
            const x = forest.pos[0] + Math.cos(phi) * r;
            let y;
            const z = forest.pos[1] + Math.sin(phi) * r;
            const gphi = Math.atan2(-z, -x);
            const gr = Math.hypot(z, x);
            let offmap = true;
            for (let l of layers) {
              const lr = l.fn(gphi);
              if (gr < lr) {
                y = l.y + h + 5;
                offmap = l === layers[2];
              }
            }
            if (offmap) continue;
            return {
              position: [x, y, z],
              size: [w, h, w],
              color: forest.color.map(
                (c) => c[0] + Math.random() * (c[1] - c[0])
              ),
            };
          }
        })
      ),
    [layers]
  );
  const treeColors = useMemo(
    () => Float32Array.from(trees.flatMap((t) => t.color)),
    [trees]
  );

  const stones = useMemo(() => {
    const p = new THREE.Vector3(41, 1, -112);
    const dir = new THREE.Vector3(-1, 0, -1);
    dir.normalize();
    dir.multiplyScalar(5);
    const up = new THREE.Vector3(0, 1, 0);
    const stones = [];
    // prettier-ignore
    const turns = [
      5, 4, 3, 4, 5, 6, 6, 5, 4, -2, -4, -8, -5, -1, 0, 3, 4, 3, 1, 2, 1, 2, 2, 0, -2, -3, -4, -7, -9, -7, -3, -2,
      0, 1, 2, 0, -2, -4, -3, 1, 4, 4, 6, 6, 4, -2, -2, -4, -4, -3, 0, 0, 0, 0, -3, -2, -3, 0, 0, 0, -3, -6, -1,
      3, 4, 2, 6, 0, 0, 0, 6, 8, 8, 6, 0, -2, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, -2, -2, -2, -2, -2, -2, -2,
      -2, -2, -2, -2, -3, -3, -3, -2, -2, -2, -2, -3, -3, -3, -3, -3, -3, -4, -4, -4, -5, -5, -6, -7, -8, -9];
    for (let i = 0; i < turns.length; ++i) {
      const gphi = Math.atan2(-p.z, -p.x);
      const gr = Math.hypot(p.z, p.x);
      for (let l of layers) {
        const lr = l.fn(gphi) + 5;
        if (gr < lr) {
          p.setY(l.y + 1);
        }
      }
      stones.push({ position: p.toArray() });
      dir.applyAxisAngle(up, 0.1 * turns[i]);
      p.add(dir);
    }
    return stones;
  }, [layers]);

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
        if (i < stage) {
          mesh.setColorAt(i, new THREE.Color(0.7, 0.7, 0.7));
        } else if (i === stage) {
          mesh.setColorAt(i, new THREE.Color(0, 0.8, 1));
        } else {
          mesh.setColorAt(i, new THREE.Color(1, 0.2, 0));
        }
      }
      mesh.instanceMatrix.needsUpdate = true;
      stoneInstances.current = mesh;
    },
    [stones, stage]
  );

  useFrame(({ camera, clock }) => {
    const t = clock.getElapsedTime();
    camera.position.z = -140;
    camera.position.y = 60 + 2 * Math.cos(0.19 * t);
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
  const heroes = [...props.heroes];
  heroes.sort((a, b) => (a.name > b.name ? 1 : -1));
  heroes.sort((a, b) => (a.level < b.level ? 1 : -1));
  return (
    <div className="HeroList">
      {heroes.map((h) => (
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
      <div
        className={'HeroCard Clickable Level' + hero.level}
        onClick={onClick}
      >
        <div className="CardBackground" />
        <div
          className="CardPortrait"
          style={{ backgroundImage: heroPortrait(hero) }}
        />
        <div className="CardName"> {hero.name} </div>
        {showLevel && (
          <div className="CardLevel">
            level <b>{hero.level}</b>
          </div>
        )}
      </div>
    </>
  );
}

function HeroCard({ hero, onFlipped }) {
  const config = { tension: 100 };
  const [flipped, setFlipped] = useState(false);
  const flip = useReactSpring({
    config,
    transform: `rotate3d(0, 1, 0, ${flipped ? 0 : 180}deg)`,
    from: { transform: 'rotate3d(0, 1, 0, 180deg)' },
  });
  const backflip = useReactSpring({
    config,
    transform: `rotate3d(0, 1, 0, ${flipped ? 180 : 360}deg)`,
    from: { transform: 'rotate3d(0, 1, 0, 360deg)' },
  });
  return (
    <>
      <animated.div
        style={backflip}
        className="CardBack Clickable"
        onClick={() => {
          setFlipped(true);
          onFlipped();
        }}
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

const HeroBodyPart = React.forwardRef(
  ({ shape, parent, children, position }, ref) => {
    ref = ref || createRef();
    const pos = new THREE.Vector3();
    const joint = new THREE.Vector3();
    if (parent) {
      joint.copy(parent.pos);
      pos.copy(parent.pos);
      if (shape.dir === 'left') {
        joint.x += parent.shape.size[0] / 2;
        pos.x = joint.x + shape.size[0] / 2;
      } else if (shape.dir === 'right') {
        joint.x -= parent.shape.size[0] / 2;
        pos.x = joint.x - shape.size[0] / 2;
      } else if (shape.dir === 'front') {
        joint.y -= parent.shape.size[1] / 2;
        pos.y = joint.y - shape.size[1] / 2;
      } else if (shape.dir === 'back') {
        joint.y += parent.shape.size[1] / 2;
        pos.y = joint.y + shape.size[1] / 2;
      } else if (shape.dir === 'up') {
        joint.z += parent.shape.size[2] / 2;
        pos.z = joint.z + shape.size[2] / 2;
      } else if (shape.dir === 'down') {
        joint.z -= parent.shape.size[2] / 2;
        pos.z = joint.z - shape.size[2] / 2;
      }
    } else {
      pos.z = shape.size[2] / 2;
    }
    if (position) {
      pos.x += position[0];
      pos.y += position[1];
    }
    const unoffset = pos.clone();
    const offset = new THREE.Vector3(...(shape.offset || [0, 0, 0]));
    pos.add(offset);
    const [, api] = useBox(
      () => ({
        mass: 5 * (shape.mass || shape.size[0] * shape.size[1] * shape.size[2]),
        position: pos.toArray(),
        args: shape.size,
      }),
      ref
    );
    useFrame(() => {
      if (ref.current) {
        ref.current.physicsApi = api;
      }
    });
    if (parent) {
      useConeTwistConstraint(parent.ref, ref, {
        pivotA: joint.clone().sub(parent.pos).add(offset).toArray(),
        pivotB: joint.clone().sub(unoffset).toArray(),
        axisA: joint.clone().sub(parent.pos).normalize().toArray(),
        axisB: joint.clone().sub(unoffset).normalize().negate().toArray(),
        twistAngle: 0,
        angle: 0,
      });
    }
    const color = shape.color || parent.color;
    return (
      <>
        <Box castShadow ref={ref} args={shape.size}>
          <meshStandardMaterial attach="material" color={color} />
          {children}
        </Box>
        {shape.children &&
          shape.children.map((c, i) => (
            <HeroBodyPart
              key={i}
              shape={c}
              parent={{ shape, ref, pos, color }}
            />
          ))}
      </>
    );
  }
);

function HeroDiorama({ hero, effects }) {
  useFrame(({ camera, clock }) => {
    const t = clock.getElapsedTime();
    camera.up.set(0, 0, 1);
    camera.position.x = -2 + 0.2 * Math.cos(t);
    camera.position.y = -2 + 0.1 * Math.sin(1.3 * t);
    camera.position.z = 2;
    camera.lookAt(0, 0, 0.5);
  });
  const ref = createRef();
  return (
    <>
      <HeroBox
        meta={hero}
        ref={ref}
        trajectory={[{ x: 0, y: 0, status: [], actions: [] }]}
        turn={0}
        turnClock={{ phase: 0 }}
        leashPos={0.0001}
      />
      <BasePlane />
    </>
  );
}

function post(url, params) {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
}

function HeroPage({ id, data, update }) {
  const hero = data.heroes.find((h) => h.id === id);
  const heroMeta = data.index[hero.name];
  function dissolve() {
    post('/dissolve', { user: 'test', hero: hero.id }).then(update);
  }
  function fuse() {
    post('/fuse', { user: 'test', hero: hero.id }).then(update);
  }
  const canFuse =
    data.heroes.filter((h) => h.name === hero.name).length > 1 &&
    data.progress.ectoplasm > 0;
  const [story, setStory] = useState(-1);
  useEffect(() => {
    return () => Howler.stop();
  }, []);
  function showStory(n) {
    setStory(n);
    Howler.stop();
    const sound = new Howl({ src: ['/sounds/' + heroMeta.story[n].voice] });
    sound.play();
  }

  function atLevelScaled(base, per_level, scale = 100) {
    return Math.round(scale * (base + hero.level * per_level));
  }

  return (
    <div className="HeroPage">
      <div className="HeroCanvas">
        <CombatCanvas effects lightPosition={[3, 0, 5]}>
          <HeroDiorama hero={heroMeta} />
        </CombatCanvas>
      </div>
      <div className="HeroText">
        <div className="HeroName"> {hero.name} </div>
        <div className="HeroStats">
          <span>{heroMeta.title}</span>
          <span>Level {hero.level}</span>
          <span>
            Max loyalty:{' '}
            {atLevelScaled(
              heroMeta.max_loyalty_base,
              heroMeta.max_loyalty_per_level
            )}
          </span>
          <span>Weight: {Math.round(50 * heroMeta.weight)}</span>
          <span>
            Speed:{' '}
            {atLevelScaled(heroMeta.speed_base, heroMeta.speed_per_level)}
          </span>
          <span>
            Influence:{' '}
            {atLevelScaled(
              heroMeta.influence_base,
              heroMeta.influence_per_level
            )}
          </span>
        </div>
        <div className="HeroPageButtons">
          <div className="HeroPageButton">
            <button disabled={data.progress.stage < 5} onClick={dissolve}>
              Dissolve into Ectoplasm
            </button>
            <p>
              Destroys this hero and yields 1 Ectoplasm.
              <br />
              Unlocked after reaching stage 5.
            </p>
          </div>
          <div className="HeroPageButton">
            <button disabled={!canFuse} onClick={fuse}>
              Fuse with Fragment
            </button>
            <p>
              Costs 1 Ectoplasm and 1 other copy of this hero.
              <br />
              Takes this hero to the next level.
            </p>
          </div>
        </div>
        <div className="HeroAbilities">
          <div className="PanelHeader">Abilities:</div>
          {heroMeta.abilities.map((a) => (
            <div
              key={a.name}
              className={
                'HeroAbility ' +
                (a.unlockLevel <= hero.level ? 'Unlocked' : 'Locked')
              }
            >
              <h1>{a.name}</h1>
              <p>
                {a.description} Unlocked at level {a.unlockLevel}.
              </p>
            </div>
          ))}
        </div>
        <div className="HeroStory">
          <div className="PanelHeader">Story:</div>
          {heroMeta.story.map((a, i) => (
            <button
              key={i}
              disabled={i >= hero.level}
              className="HeroStoryButton"
              onClick={() => showStory(i)}
            >
              {i >= hero.level
                ? `Unlocked at level ${i + 1}`
                : `Diary ${i + 1} ${heroMeta.story[i].voice ? '🔊' : ''}`}
            </button>
          ))}
          {story >= 0 && (
            <p className="HeroStoryText">{heroMeta.story[story].text}</p>
          )}
        </div>
      </div>
    </div>
  );
}

function Searched(props) {
  useEffect(() => window.scrollTo(0, 0), []);
  return (
    <div className="Searched">
      <HeroCard
        onFlipped={() => props.setShowButtons(true)}
        hero={props.data.just_found}
      ></HeroCard>
    </div>
  );
}

function fetchData(setData, setError) {
  fetch('/getuserdata?user=test')
    .then((res) => res.json())
    .then(
      (res) => setData(res),
      (error) => setError(error)
    );
}

function App() {
  const [page, setPage] = useState('map');
  const [heroPage, setHeroPage] = useState();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [showButtons, setShowButtons] = useState(true);
  useEffect(() => fetchData(setData, setError), []);
  function searchBeach() {
    post('/searchbeach', { user: 'test' })
      .then((res) => res.json())
      .then(
        (res) => {
          setData(res);
          setPage('searched');
          setShowButtons(false);
        },
        (error) => setError(error)
      );
  }
  function update() {
    fetchData((data) => {
      if (page === 'hero' && !data.heroes.find((h) => h.id === heroPage)) {
        setPage('heroes');
      }
      setData(data);
    }, setError);
  }

  return (
    <div>
      {error && <div>{error}</div>}
      {data && (
        <div>
          <div className="TopStats">
            <span>
              {data.progress.stage >= 5 &&
                `Ectoplasm: ${data.progress.ectoplasm}`}
            </span>
            <span>Day {data.progress.day}</span>
            <span>Next stage: {data.progress.stage + 1}</span>
          </div>
          {page === 'combat' && (
            <Combat data={data} setShowButtons={setShowButtons} />
          )}
          {page === 'map' && (
            <Map setPage={setPage} searchBeach={searchBeach} data={data} />
          )}
          {page === 'heroes' && (
            <HeroList
              heroes={data.heroes}
              onClick={(h) => {
                setPage('hero');
                setHeroPage(h.id);
              }}
            />
          )}
          {page === 'hero' && (
            <HeroPage update={update} id={heroPage} data={data} />
          )}
          {page === 'searched' && (
            <Searched data={data} setShowButtons={setShowButtons} />
          )}
        </div>
      )}
      {showButtons && (
        <div>
          <button onClick={() => setPage('heroes')}>Heroes</button>
          <button
            onClick={() => {
              update();
              setPage('map');
            }}
          >
            Map
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
