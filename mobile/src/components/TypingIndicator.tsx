import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, View } from 'react-native';
import { colors, spacing } from '../theme';

export function TypingIndicator() {
  // Animation values for each dot
  const dot1Scale = useRef(new Animated.Value(0.6)).current;
  const dot2Scale = useRef(new Animated.Value(0.6)).current;
  const dot3Scale = useRef(new Animated.Value(0.6)).current;

  // Container entrance animation
  const containerOpacity = useRef(new Animated.Value(0)).current;
  const containerSlide = useRef(new Animated.Value(10)).current;

  useEffect(() => {
    // Entrance animation
    Animated.parallel([
      Animated.timing(containerOpacity, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true,
      }),
      Animated.spring(containerSlide, {
        toValue: 0,
        friction: 8,
        tension: 100,
        useNativeDriver: true,
      }),
    ]).start();

    // Bouncing dots animation
    const animateDot = (dot: Animated.Value, delay: number) =>
      Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.spring(dot, {
            toValue: 1.2,
            friction: 3,
            tension: 200,
            useNativeDriver: true,
          }),
          Animated.spring(dot, {
            toValue: 0.6,
            friction: 3,
            tension: 200,
            useNativeDriver: true,
          }),
        ])
      );

    const a1 = animateDot(dot1Scale, 0);
    const a2 = animateDot(dot2Scale, 150);
    const a3 = animateDot(dot3Scale, 300);

    a1.start();
    a2.start();
    a3.start();

    return () => {
      a1.stop();
      a2.stop();
      a3.stop();
    };
  }, []);

  const dots = [dot1Scale, dot2Scale, dot3Scale];

  return (
    <Animated.View
      style={[
        styles.container,
        {
          opacity: containerOpacity,
          transform: [{ translateY: containerSlide }],
        },
      ]}
    >
      <View style={styles.bubble}>
        {dots.map((scale, i) => (
          <Animated.View
            key={i}
            style={[
              styles.dot,
              {
                transform: [{ scale }],
              },
            ]}
          />
        ))}
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    alignItems: 'flex-start',
  },
  bubble: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm + 4,
    gap: 6,
    // Subtle shadow for depth
    shadowColor: colors.accent,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.accent,
  },
});
