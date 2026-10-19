<template>
  <div id="music-player" v-if="tracks.length">
    <div class="player-track-name">{{ currentTrack?.title }}</div>
    <div class="player-controls">
      <button class="player-btn" @click="togglePlay">{{ isPaused ? "▶" : "⏸" }}</button>
      <button class="player-btn" @click="nextTrack">⏭</button>
      <input
        type="range"
        class="player-volume"
        min="0"
        max="1"
        step="0.05"
        v-model="volume"
        @input="setVolume"
      />
    </div>

    <audio
      ref="audioPlayer"
      crossorigin="anonymous"
      @ended="nextTrack"
      @play="isPaused = false"
      @pause="isPaused = true"
    ></audio>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue";
import api from "../api";

const tracks = ref([]);
const currentIndex = ref(0);
const isPaused = ref(true);
const volume = ref(0.5);
const audioPlayer = ref(null);

const currentTrack = computed(() => tracks.value[currentIndex.value]);
const currentTrackUrl = computed(() => {
  if (!currentTrack.value || !currentTrack.value.file) return "";
  if (currentTrack.value.file.startsWith("http")) return currentTrack.value.file;
  return `http://127.0.0.1:8000${currentTrack.value.file}`;
});

const playCurrent = async () => {
  if (!audioPlayer.value) return;
  audioPlayer.value.src = currentTrackUrl.value;
  audioPlayer.value.volume = volume.value;
  try {
    await audioPlayer.value.play();
  } catch (e) {
    console.error("Браузер заблокировал автоплей:", e);
  }
};

const togglePlay = async () => {
  if (!audioPlayer.value) return;

  if (!audioPlayer.value.src) {
    await playCurrent();
    return;
  }

  if (audioPlayer.value.paused) {
    await audioPlayer.value.play();
  } else {
    audioPlayer.value.pause();
  }
};

const nextTrack = () => {
  currentIndex.value = (currentIndex.value + 1) % tracks.value.length;
  setTimeout(() => {
    playCurrent();
  }, 100);
};

const setVolume = () => {
  if (audioPlayer.value) audioPlayer.value.volume = volume.value;
};

watch(currentTrackUrl, () => {
  if (audioPlayer.value && !isPaused.value) {
    playCurrent();
  }
});

onMounted(async () => {
  try {
    const res = await api.get("music/");
    tracks.value = res.data;
  } catch (error) {
    console.error("Ошибка загрузки музыки:", error);
  }
});
</script>
