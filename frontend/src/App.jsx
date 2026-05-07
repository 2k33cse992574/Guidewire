import React, { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars } from '@react-three/drei'

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

function PremiumCalculator() {
  const [weeklyIncome, setWeeklyIncome] = useState(4200);
  const [riskScore, setRiskScore] = useState(0.6);

  const premium = (weeklyIncome * riskScore * 0.05).toFixed(2);

  return (
    <div style={{
      position: 'absolute', top: '120px', left: '20px', zIndex: 10,
      background: 'rgba(0, 0, 0, 0.7)', border: '1px solid #00ffcc',
      padding: '20px', borderRadius: '15px', color: '#fff',
      fontFamily: 'sans-serif', maxWidth: '300px',
      boxShadow: '0 0 15px rgba(0, 255, 204, 0.3)'
    }}>
      <h3 style={{ margin: '0 0 10px 0', color: '#00ffcc' }}>Dynamic Premium Calculator</h3>
      <p style={{ fontSize: '12px', color: '#aaa', margin: '0 0 15px 0' }}>
        Formula: Premium = Weekly Income × Risk Score × 0.05
      </p>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', fontSize: '14px', marginBottom: '5px' }}>
          Weekly Income: ₹{weeklyIncome}
        </label>
        <input 
          type="range" min="1000" max="10000" step="100" 
          value={weeklyIncome} 
          onChange={(e) => setWeeklyIncome(Number(e.target.value))} 
          style={{ width: '100%' }}
        />
      </div>

      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', fontSize: '14px', marginBottom: '5px' }}>
          AI Risk Score: {riskScore}
        </label>
        <input 
          type="range" min="0.1" max="1.0" step="0.1" 
          value={riskScore} 
          onChange={(e) => setRiskScore(Number(e.target.value))} 
          style={{ width: '100%' }}
        />
      </div>

      <div style={{ 
        background: 'rgba(0, 255, 204, 0.1)', padding: '10px', 
        borderRadius: '8px', textAlign: 'center', border: '1px solid #00ffcc'
      }}>
        <strong style={{ fontSize: '14px', color: '#00ffcc' }}>Weekly Premium</strong>
        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>₹{premium}</div>
      </div>
    </div>
  )
}

function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#0a0a0a', display: 'flex', flexDirection: 'column' }}>
      <div style={{ position: 'absolute', top: '20px', left: '0', width: '100%', textAlign: 'center', zIndex: 10 }}>
        <h1 style={{ color: '#00ffcc', fontFamily: 'sans-serif', margin: 0, textShadow: '0 0 10px #00ffcc' }}>GigShield 3D Gateway</h1>
        <p style={{ color: '#ffffff', fontFamily: 'sans-serif' }}>AI-Powered Parametric Insurance</p>
      </div>

      <PremiumCalculator />
      
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
            transition: 'transform 0.2s',
            display: 'inline-block'
          }}
        >
          ENTER GIGSHIELD DASHBOARD
        </a>
      </div>
    </div>
  )
}

export default App
