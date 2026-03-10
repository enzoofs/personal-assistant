import React, { useEffect, useMemo, useRef } from 'react';
import { Animated, Dimensions, StyleSheet, View } from 'react-native';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

const PARTICLE_COUNT = 50;
const COLORS = [
  '#FF6B6B', // Red
  '#4ECDC4', // Teal
  '#FFE66D', // Yellow
  '#95E1D3', // Mint
  '#F38181', // Coral
  '#AA96DA', // Purple
  '#58A6FF', // Blue (accent)
  '#3FB950', // Green (success)
];

interface Particle {
  x: number;
  y: number;
  color: string;
  size: number;
  rotation: number;
  shape: 'square' | 'circle' | 'rectangle';
}

interface Props {
  active: boolean;
  onComplete?: () => void;
  originY?: number; // Y position to start from (default: top)
}

export function Confetti({ active, onComplete, originY = 0 }: Props) {
  // Generate random particles
  const particles = useMemo<Particle[]>(() => {
    return Array.from({ length: PARTICLE_COUNT }, () => ({
      x: Math.random() * SCREEN_WIDTH,
      y: originY - 50 - Math.random() * 100, // Start above the origin
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      size: 6 + Math.random() * 8,
      rotation: Math.random() * 360,
      shape: ['square', 'circle', 'rectangle'][Math.floor(Math.random() * 3)] as Particle['shape'],
    }));
  }, [active, originY]);

  // Animation values
  const animations = useRef(
    particles.map(() => ({
      translateY: new Animated.Value(0),
      translateX: new Animated.Value(0),
      rotate: new Animated.Value(0),
      opacity: new Animated.Value(1),
      scale: new Animated.Value(0),
    }))
  ).current;

  useEffect(() => {
    if (active) {
      // Reset and start animations
      animations.forEach((anim, index) => {
        // Reset values
        anim.translateY.setValue(0);
        anim.translateX.setValue(0);
        anim.rotate.setValue(0);
        anim.opacity.setValue(1);
        anim.scale.setValue(0);

        const delay = Math.random() * 200;
        const duration = 1500 + Math.random() * 1000;
        const horizontalMovement = (Math.random() - 0.5) * 200;
        const rotations = 2 + Math.random() * 4;

        // Pop in
        Animated.timing(anim.scale, {
          toValue: 1,
          duration: 150,
          delay,
          useNativeDriver: true,
        }).start();

        // Fall down
        Animated.timing(anim.translateY, {
          toValue: SCREEN_HEIGHT + 100,
          duration,
          delay,
          useNativeDriver: true,
        }).start();

        // Horizontal drift
        Animated.timing(anim.translateX, {
          toValue: horizontalMovement,
          duration,
          delay,
          useNativeDriver: true,
        }).start();

        // Rotation
        Animated.timing(anim.rotate, {
          toValue: rotations,
          duration,
          delay,
          useNativeDriver: true,
        }).start();

        // Fade out near the end
        Animated.timing(anim.opacity, {
          toValue: 0,
          duration: duration * 0.3,
          delay: delay + duration * 0.7,
          useNativeDriver: true,
        }).start(() => {
          if (index === 0 && onComplete) {
            onComplete();
          }
        });
      });
    }
  }, [active]);

  if (!active) return null;

  return (
    <View style={styles.container} pointerEvents="none">
      {particles.map((particle, index) => {
        const anim = animations[index];
        const rotation = anim.rotate.interpolate({
          inputRange: [0, 1],
          outputRange: ['0deg', '360deg'],
        });

        return (
          <Animated.View
            key={index}
            style={[
              styles.particle,
              {
                left: particle.x,
                top: particle.y,
                width: particle.shape === 'rectangle' ? particle.size * 1.5 : particle.size,
                height: particle.shape === 'rectangle' ? particle.size * 0.6 : particle.size,
                backgroundColor: particle.color,
                borderRadius: particle.shape === 'circle' ? particle.size / 2 : 2,
                opacity: anim.opacity,
                transform: [
                  { translateY: anim.translateY },
                  { translateX: anim.translateX },
                  { rotate: rotation },
                  { scale: anim.scale },
                ],
              },
            ]}
          />
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    zIndex: 1000,
  },
  particle: {
    position: 'absolute',
  },
});
