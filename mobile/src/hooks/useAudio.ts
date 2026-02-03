import { useCallback, useRef, useState } from 'react';
import { Audio } from 'expo-av';
import { Platform } from 'react-native';
import * as FileSystem from 'expo-file-system/legacy';

export function useAudio() {
  const [recording, setRecording] = useState(false);
  const [playing, setPlaying] = useState(false);
  const recordingRef = useRef<Audio.Recording | null>(null);
  const soundRef = useRef<Audio.Sound | null>(null);

  const startRecording = useCallback(async (): Promise<void> => {
    await Audio.requestPermissionsAsync();
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      playsInSilentModeIOS: true,
    });

    const { recording } = await Audio.Recording.createAsync(
      Audio.RecordingOptionsPresets.HIGH_QUALITY
    );
    recordingRef.current = recording;
    setRecording(true);
  }, []);

  const stopRecording = useCallback(async (): Promise<string | null> => {
    if (!recordingRef.current) return null;

    setRecording(false);
    await recordingRef.current.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({ allowsRecordingIOS: false });

    const uri = recordingRef.current.getURI();
    recordingRef.current = null;
    return uri;
  }, []);

  const playBase64Audio = useCallback(async (base64: string): Promise<void> => {
    try {
      // Write base64 to temp file
      const fileUri = FileSystem.cacheDirectory + 'atlas_response.mp3';
      await FileSystem.writeAsStringAsync(fileUri, base64, {
        encoding: 'base64',
      });

      if (soundRef.current) {
        await soundRef.current.unloadAsync();
      }

      const { sound } = await Audio.Sound.createAsync({ uri: fileUri });
      soundRef.current = sound;
      setPlaying(true);

      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          setPlaying(false);
        }
      });

      await sound.setRateAsync(1.25, true);
      await sound.playAsync();
    } catch (err) {
      setPlaying(false);
      console.error('Playback error:', err);
    }
  }, []);

  return { recording, playing, startRecording, stopRecording, playBase64Audio };
}
