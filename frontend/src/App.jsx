import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars, Text } from '@react-three/drei'
import './App.css'

function Shield() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    meshRef.current.rotation.y += delta * 0.5
    meshRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.2
  })

  return (
    <mesh ref={meshRef}>
      <octahedronGeometry args={[1.5, 0]} />
      <meshStandardMaterial color="#00ffcc" wireframe />
      <meshStandardMaterial color="#002244" transparent opacity={0.8} />
    </mesh>
  )
}

function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#0a0a0a', display: 'flex', flexDirection: 'column' }}>
      <div style={{ position: 'absolute', top: '20px', left: '0', width: '100%', textAlign: 'center', zIndex: 10 }}>
        <h1 style={{ color: '#00ffcc', fontFamily: 'sans-serif', margin: 0, textShadow: '0 0 10px #00ffcc' }}>GigShield 3D Gateway</h1>
        <p style={{ color: '#ffffff', fontFamily: 'sans-serif' }}>AI-Powered Parametric Insurance</p>
      </div>
      
      <div style={{ flex: 1 }}>
        <Canvas camera={{ position: [0, 0, 5] }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} color="#00ffcc" />
          <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
          <Shield />
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={1} />
        </Canvas>
      </div>

      <div style={{ position: 'absolute', bottom: '50px', left: '0', width: '100%', textAlign: 'center', zIndex: 10 }}>
        <a 
          href="/index.html" 
          style={{
            padding: '15px 30px',
            background: 'linear-gradient(90deg, #00ffcc, #0088ff)',
            color: '#000',
            textDecoration: 'none',
            fontSize: '18px',
            fontWeight: 'bold',
            borderRadius: '25px',
            fontFamily: 'sans-serif',
            boxShadow: '0 0 20px rgba(0, 255, 204, 0.5)',
            transition: 'transform 0.2s'
          }}
        >
          ENTER GIGSHIELD DASHBOARD
        </a>
      </div>
    </div>
  )
}

export default App
