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
        dist = 0.2 * length(position);
        float theta = sin(10.0 * time + dist) / 100.0;
        float c = cos(theta);
        float s = sin(theta);
        mat3 m = mat3(c, 0, s, 0, 1, 0, -s, 0, c);
        vec3 transformed = vec3(position) * m;
      `
      );
      shader.fragmentShader = `
        varying float dist;
        ${shader.fragmentShader}
      `;
      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <alphamap_fragment>',
        `
        diffuseColor.a = atan(0.1 * (30.0 - dist)) + 0.9;
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
