import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, View } from 'react-native';
import { colors } from '../theme';

const NUM_BARS = 24;
const BAR_WIDTH = 3;
const BAR_GAP = 3;
const MIN_HEIGHT = 4;
const MAX_HEIGHT = 60;

interface Props {
  active?: boolean;
}

export function VoiceWaveform({ active = false }: Props) {
  // Create animated values for each bar
  const bars = useRef(
    Array.from({ length: NUM_BARS }, () => new Animated.Value(MIN_HEIGHT))
  ).current;

  // Track animation references for cleanup
  const animations = useRef<Animated.CompositeAnimation[]>([]);

  useEffect(() => {
    if (active) {
      // Start animating each bar with random durations and heights
      animations.current = bars.map((bar, index) => {
        const animate = () => {
          // Random target height
          const targetHeight = MIN_HEIGHT + Math.random() * (MAX_HEIGHT - MIN_HEIGHT);
          // Random duration for organic feel
          const duration = 80 + Math.random() * 120;

          return Animated.sequence([
            Animated.timing(bar, {
              toValue: targetHeight,
              duration,
              useNativeDriver: false, // height can't use native driver
            }),
            Animated.timing(bar, {
              toValue: MIN_HEIGHT + Math.random() * 15,
              duration: duration * 0.8,
              useNativeDriver: false,
            }),
          ]);
        };

        // Create looping animation
        const loop = Animated.loop(animate());

        // Stagger start times for wave effect
        setTimeout(() => loop.start(), index * 30);

        return loop;
      });
    } else {
      // Stop all animations and reset
      animations.current.forEach(anim => anim.stop());
      bars.forEach(bar => {
        Animated.timing(bar, {
          toValue: MIN_HEIGHT,
          duration: 200,
          useNativeDriver: false,
        }).start();
      });
    }

    return () => {
      animations.current.forEach(anim => anim.stop());
    };
  }, [active, bars]);

  return (
    <View style={styles.container}>
      {bars.map((height, index) => {
        // Create gradient effect - center bars are brighter
        const distanceFromCenter = Math.abs(index - NUM_BARS / 2) / (NUM_BARS / 2);
        const opacity = 0.4 + (1 - distanceFromCenter) * 0.6;

        return (
          <Animated.View
            key={index}
            style={[
              styles.bar,
              {
                height,
                opacity: active ? opacity : 0.3,
                backgroundColor: active ? colors.accent : colors.textSecondary,
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: MAX_HEIGHT + 20,
    gap: BAR_GAP,
  },
  bar: {
    width: BAR_WIDTH,
    borderRadius: BAR_WIDTH / 2,
  },
});
