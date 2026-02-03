import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

/**
 * Centralized haptic feedback utilities.
 *
 * Uses expo-haptics for refined tactile feedback on iOS and Android.
 * Gracefully handles platforms that don't support haptics.
 */

// Check if haptics are supported
const isHapticsSupported = Platform.OS === 'ios' || Platform.OS === 'android';

/**
 * Light impact - for subtle interactions like hovering or light taps
 */
export async function lightImpact(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  } catch {
    // Silently fail if haptics not available
  }
}

/**
 * Medium impact - for standard button presses and selections
 */
export async function mediumImpact(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  } catch {
    // Silently fail
  }
}

/**
 * Heavy impact - for significant actions like confirmations or deletions
 */
export async function heavyImpact(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
  } catch {
    // Silently fail
  }
}

/**
 * Selection feedback - for picker/selection changes
 */
export async function selection(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.selectionAsync();
  } catch {
    // Silently fail
  }
}

/**
 * Success notification - for completed actions
 */
export async function success(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  } catch {
    // Silently fail
  }
}

/**
 * Warning notification - for warnings or important notices
 */
export async function warning(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
  } catch {
    // Silently fail
  }
}

/**
 * Error notification - for errors or failures
 */
export async function error(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
  } catch {
    // Silently fail
  }
}

/**
 * Custom pattern - for special celebrations or unique feedback
 * Creates a rhythmic pattern of impacts
 */
export async function celebration(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    await delay(50);
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    await delay(50);
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    await delay(100);
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  } catch {
    // Silently fail
  }
}

/**
 * Recording start - distinctive pattern for voice recording
 */
export async function recordingStart(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    await delay(100);
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  } catch {
    // Silently fail
  }
}

/**
 * Recording stop - feedback when stopping recording
 */
export async function recordingStop(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
  } catch {
    // Silently fail
  }
}

/**
 * Message sent - subtle feedback when sending a message
 */
export async function messageSent(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  } catch {
    // Silently fail
  }
}

/**
 * Tab change - light feedback for navigation
 */
export async function tabChange(): Promise<void> {
  if (!isHapticsSupported) return;
  try {
    await Haptics.selectionAsync();
  } catch {
    // Silently fail
  }
}

// Helper function
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Export all as a namespace-like object for convenient access
export const Haptic = {
  light: lightImpact,
  medium: mediumImpact,
  heavy: heavyImpact,
  selection,
  success,
  warning,
  error,
  celebration,
  recordingStart,
  recordingStop,
  messageSent,
  tabChange,
};
