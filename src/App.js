import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from 'react-three-fiber';
import './App.css';

// Copied from example.
function Box(props) {
  // This reference will give us direct access to the mesh
  const mesh = useRef();
  var stage = useRef({x: 0});

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
    mesh.current.position.y = Math.abs(Math.sin(Math.PI * stage.current.x / 60) * 2);  
    mesh.current.rotation.x = mesh.current.rotation.y += 0.01
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


function PartySelector({data, startCombat}) {
  // TODO: let the user set the party
  const [party, setParty] = useState([
    data.heroes[0].id,
    data.heroes[0].id,
    data.heroes[0].id,
    data.heroes[0].id,
    data.heroes[0].id
  ]);

  return (
    <div>
      {party.map((id) => {
        const h = data.heroes.find(hero => hero.id === id);
        return <Hero hero={h} key={id}/>
      })}
      <button onClick={() => startCombat(party)}>Gooooooooooooo!</button>
    </div>
  )
}

function BattleRenderer() {
  return (
    <Canvas>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <Box position={[-1.2, 0, 0]} />
      <Box position={[1.2, 0, 0]} />
    </Canvas>
  )
}


function Spinner() {
  return <div/>
}


function Combat({data}) {
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
  }, [state])

  return (
    <div>
      { state === 'selectParty' && <PartySelector data={data} startCombat={startCombat}/> }
      { state === 'simulate' && <Spinner/> }
      { state === 'renderBattle' && <BattleRenderer/> }
    </div>
  )
}

function Map(props) {
  return (
    <div>
      <p>day {props.data.progress.day}</p>
      <p>current stage: {props.data.progress.stage}</p>
      <p>
        <button onClick={props.searchBeach}>search the beach</button>
        <button onClick={() => props.setPage('combat')}>attack</button>
      </p>
    </div>
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
