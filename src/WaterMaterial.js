import { MeshStandardMaterial } from 'three';
import React, { useMemo } from 'react';
import { useFrame } from 'react-three-fiber';

export default React.forwardRef(({ ...props }: Props, ref) => {
  const material = useMemo(() => {
    const m = new MeshStandardMaterial();
    m.time = { value: 0 };
    m.onBeforeCompile = function (shader) {
      shader.uniforms.time = m.time;
      shader.vertexShader = `
        uniform float time;
        varying float dist;
        ${shader.vertexShader}
      `;
      shader.vertexShader = shader.vertexShader.replace(
        '#include <begin_vertex>',
        `
        dist = length(position);
        vec3 transformed = vec3(position);
        transformed.z = 0.5 * sin(5.0 * time + 0.2 * dist);
      `
      );
      shader.fragmentShader = `
        varying float dist;
        ${shader.fragmentShader}
      `;
      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <alphamap_fragment>',
        `
        totalEmissiveRadiance += 0.5 * PI - atan(0.05 * (250.0 - dist));
      `
      );
    };
    return m;
  }, []);
  useFrame(
    ({ clock }) => material && (material.time.value = clock.getElapsedTime())
  );
  return (
    <primitive
      dispose={null}
      object={material}
      ref={ref}
      attach="material"
      color="#169"
      roughness={0.2}
    />
  );
});
