import React, { useRef, useState, useEffect } from 'react'
import { Canvas, useFrame } from 'react-three-fiber';
import './App.css';

// Copied from example.
function Box(props) {
  // This reference will give us direct access to the mesh
  const mesh = useRef()

  // Set up state for the hovered and active state
  const [hovered, setHover] = useState(false)
  const [active, setActive] = useState(false)

  // Rotate mesh every frame, this is outside of React without overhead
  useFrame(() => (mesh.current.rotation.x = mesh.current.rotation.y += 0.01))

  return (
    <mesh
      {...props}
      ref={mesh}
      scale={active ? [1.5, 1.5, 1.5] : [1, 1, 1]}
      onClick={(e) => setActive(!active)}
      onPointerOver={(e) => setHover(true)}
      onPointerOut={(e) => setHover(false)}>
      <boxBufferGeometry attach="geometry" args={[1, 1, 1]} />
      <meshStandardMaterial attach="material" color={hovered ? 'hotpink' : 'orange'} />
    </mesh>
  )
}
function Combat() {
  return <div>
    <Canvas>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <Box position={[-1.2, 0, 0]} />
      <Box position={[1.2, 0, 0]} />
    </Canvas>;
  </div>;
}

function Map(props) {
  console.log(props);
  return <div>
    current stage: {props.data.progress.stage}
  </div>;
}

function Heroes(props) {
  return <div>
    { props.data.heroes.map(h =>
    <div key={h.hero}>
      {h.hero}, level {h.level}
    </div>) }
  </div>;
}

function App() {
  const [currentPage, setCurrentPage] = useState('map');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    fetch('/getuserdata?user=test')
    .then(res => res.json())
    .then(
      res => setData(res),
      error => setError(error))
  }, []);

  return (
    <div>
    { currentPage }
      { error && <div>{error}</div> }
      { data && <div>
          { JSON.stringify(data) }
          { currentPage === 'combat' && <Combat setPage={setCurrentPage} data={data}></Combat> }
          { currentPage === 'map' && <Map setPage={setCurrentPage} data={data}></Map> }
          { currentPage === 'heroes' && <Heroes setPage={setCurrentPage} data={data}></Heroes> }
        </div> }
      <div>
        <button onClick={() => setCurrentPage('heroes')}>heroes</button>
        <button onClick={() => setCurrentPage('map')}>map</button>
        <button onClick={() => setCurrentPage('combat')}>attack</button>
      </div>
    </div>
  );
}

export default App;
