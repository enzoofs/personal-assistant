import React, { useEffect, useRef, useState } from 'react';
import {
  Animated,
  Modal,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme';
import { VoiceWaveform } from './VoiceWaveform';
import { Haptic } from '../utils/haptics';

interface Props {
  onPress: () => void;
  disabled?: boolean;
  recording?: boolean;
}

export function MicButton({ onPress, disabled, recording }: Props) {
  // Pulse animation for recording button
  const pulseScale = useRef(new Animated.Value(1)).current;
  const pulseOpacity = useRef(new Animated.Value(0.5)).current;

  // Glow animation
  const glowScale = useRef(new Animated.Value(1)).current;

  // Recording dot blink
  const dotOpacity = useRef(new Animated.Value(1)).current;

  // Recording duration
  const [duration, setDuration] = useState(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Button entrance animation
  const buttonScale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (recording) {
      // Start pulse animation
      Animated.loop(
        Animated.parallel([
          Animated.sequence([
            Animated.timing(pulseScale, {
              toValue: 1.8,
              duration: 1000,
              useNativeDriver: true,
            }),
            Animated.timing(pulseScale, {
              toValue: 1,
              duration: 0,
              useNativeDriver: true,
            }),
          ]),
          Animated.sequence([
            Animated.timing(pulseOpacity, {
              toValue: 0,
              duration: 1000,
              useNativeDriver: true,
            }),
            Animated.timing(pulseOpacity, {
              toValue: 0.5,
              duration: 0,
              useNativeDriver: true,
            }),
          ]),
        ])
      ).start();

      // Glow animation
      Animated.loop(
        Animated.sequence([
          Animated.timing(glowScale, {
            toValue: 1.15,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(glowScale, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
        ])
      ).start();

      // Recording dot blink
      Animated.loop(
        Animated.sequence([
          Animated.timing(dotOpacity, {
            toValue: 0.3,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(dotOpacity, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();

      // Start timer
      setDuration(0);
      timerRef.current = setInterval(() => {
        setDuration(d => d + 1);
      }, 1000);
    } else {
      // Reset animations
      pulseScale.setValue(1);
      pulseOpacity.setValue(0.5);
      glowScale.setValue(1);
      dotOpacity.setValue(1);

      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      setDuration(0);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [recording]);

  const handlePress = () => {
    // Refined haptic feedback based on state
    if (recording) {
      Haptic.recordingStop();
    } else {
      Haptic.recordingStart();
    }

    // Button press animation
    Animated.sequence([
      Animated.timing(buttonScale, {
        toValue: 0.9,
        duration: 50,
        useNativeDriver: true,
      }),
      Animated.spring(buttonScale, {
        toValue: 1,
        friction: 3,
        tension: 200,
        useNativeDriver: true,
      }),
    ]).start();

    onPress();
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Normal (not recording) button
  if (!recording) {
    return (
      <View style={styles.container}>
        <Animated.View style={{ transform: [{ scale: buttonScale }] }}>
          <Pressable
            style={[styles.button, disabled && styles.buttonDisabled]}
            onPress={handlePress}
            disabled={disabled}
          >
            <Ionicons
              name="mic-outline"
              size={28}
              color={disabled ? colors.textSecondary : colors.text}
            />
          </Pressable>
        </Animated.View>
      </View>
    );
  }

  // Recording overlay with waveform
  return (
    <Modal transparent animationType="fade" visible>
      <View style={styles.overlay}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.recordingIndicator}>
            <Animated.View style={[styles.recordingDot, { opacity: dotOpacity }]} />
            <Text style={styles.recordingText}>Gravando</Text>
          </View>
          <Text style={styles.duration}>{formatDuration(duration)}</Text>
        </View>

        {/* Waveform */}
        <View style={styles.waveformContainer}>
          <VoiceWaveform active />
        </View>

        {/* Instructions */}
        <Text style={styles.instruction}>Toque para enviar</Text>

        {/* Stop Button with pulse */}
        <View style={styles.buttonContainer}>
          {/* Pulse ring */}
          <Animated.View
            style={[
              styles.pulseRing,
              {
                transform: [{ scale: pulseScale }],
                opacity: pulseOpacity,
              },
            ]}
          />

          {/* Glow effect */}
          <Animated.View
            style={[
              styles.glowRing,
              { transform: [{ scale: glowScale }] },
            ]}
          />

          {/* Main button */}
          <Pressable style={styles.buttonRecording} onPress={handlePress}>
            <Ionicons name="stop" size={32} color={colors.text} />
          </Pressable>
        </View>

        {/* Cancel hint */}
        <Text style={styles.cancelHint}>Deslize para baixo para cancelar</Text>
      </View>
    </Modal>
  );
}

const SIZE = 80;

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.sm,
  },
  button: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.accent,
    alignItems: 'center',
    justifyContent: 'center',
    // Shadow
    shadowColor: colors.accent,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  buttonDisabled: {
    backgroundColor: colors.surfaceLight,
    shadowOpacity: 0,
    elevation: 0,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(13, 17, 23, 0.95)',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.xl,
  },
  header: {
    position: 'absolute',
    top: 80,
    alignItems: 'center',
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  recordingDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: colors.error,
  },
  recordingText: {
    color: colors.error,
    fontSize: fontSize.md,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 2,
  },
  duration: {
    color: colors.text,
    fontSize: fontSize.xxl,
    fontWeight: '300',
    fontVariant: ['tabular-nums'],
  },
  waveformContainer: {
    marginBottom: spacing.xl,
  },
  instruction: {
    color: colors.textSecondary,
    fontSize: fontSize.md,
    marginBottom: spacing.xl,
  },
  buttonContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    width: SIZE * 2,
    height: SIZE * 2,
  },
  pulseRing: {
    position: 'absolute',
    width: SIZE,
    height: SIZE,
    borderRadius: SIZE / 2,
    backgroundColor: colors.error,
  },
  glowRing: {
    position: 'absolute',
    width: SIZE + 20,
    height: SIZE + 20,
    borderRadius: (SIZE + 20) / 2,
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: colors.error,
    opacity: 0.3,
  },
  buttonRecording: {
    width: SIZE,
    height: SIZE,
    borderRadius: SIZE / 2,
    backgroundColor: colors.error,
    alignItems: 'center',
    justifyContent: 'center',
    // Shadow
    shadowColor: colors.error,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 16,
    elevation: 8,
  },
  cancelHint: {
    position: 'absolute',
    bottom: 60,
    color: colors.textSecondary,
    fontSize: fontSize.sm,
  },
});
