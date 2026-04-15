(function () {
    var tracks = window.BRAT_TRACKS || [];
    if (tracks.length === 0) return;

    var STORAGE_KEY = 'brat_player';

    var state = {
        index: 0,
        time: 0,
        muted: false,
        volume: 0.5,
        paused: false
    };

    try {
        var saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
        if (saved) {
            state.index  = saved.index  || 0;
            state.time   = saved.time   || 0;
            state.muted  = saved.muted  || false;
            state.volume = (saved.volume !== undefined) ? saved.volume : 0.5;
            state.paused = saved.paused || false;
        }
    } catch (e) {}

    var audio = new Audio();
    audio.volume = state.muted ? 0 : state.volume;

    function saveState() {
        try {
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
                index:  state.index,
                time:   audio.currentTime,
                muted:  state.muted,
                volume: state.volume,
                paused: state.paused
            }));
        } catch (e) {}
    }

    function updateUI() {
        var nameEl   = document.getElementById('track-name');
        var muteBtn  = document.getElementById('mute-btn');
        var pauseBtn = document.getElementById('pause-btn');
        var volSlider = document.getElementById('vol-slider');

        if (nameEl)   nameEl.textContent = tracks[state.index].name;
        if (muteBtn)  muteBtn.textContent = state.muted ? '🔇' : '🔊';
        if (pauseBtn) pauseBtn.textContent = (audio.paused && !state.paused === false) ? '▶' : (state.paused ? '▶' : '⏸');
        if (volSlider) volSlider.value = state.muted ? 0 : state.volume;
    }

    function loadTrack(index, startTime, autoplay) {
        state.index = index;
        audio.src = tracks[index].url;
        audio.currentTime = startTime || 0;
        audio.volume = state.muted ? 0 : state.volume;

        if (!state.paused && autoplay !== false) {
            audio.play().catch(function () {
                document.addEventListener('click', function startOnClick() {
                    if (!state.paused) audio.play();
                    document.removeEventListener('click', startOnClick);
                });
            });
        }
        updateUI();
    }

    function nextTrack() {
        state.index = (state.index + 1) % tracks.length;
        state.paused = false;
        loadTrack(state.index, 0, true);
        saveState();
    }

    function togglePause() {
        if (audio.paused) {
            state.paused = false;
            audio.play();
        } else {
            state.paused = true;
            audio.pause();
        }
        updateUI();
        saveState();
    }

    function toggleMute() {
        state.muted = !state.muted;
        audio.volume = state.muted ? 0 : state.volume;
        var volSlider = document.getElementById('vol-slider');
        if (volSlider) volSlider.value = state.muted ? 0 : state.volume;
        updateUI();
        saveState();
    }

    function setVolume(val) {
        state.volume = parseFloat(val);
        state.muted = state.volume === 0;
        audio.volume = state.volume;
        updateUI();
        saveState();
    }

    window.addEventListener('beforeunload', function () {
        state.paused = audio.paused;
        saveState();
    });

    setInterval(function () {
        if (!audio.paused) saveState();
    }, 1000);

    audio.addEventListener('ended', nextTrack);

    window.bratNextTrack  = nextTrack;
    window.bratToggleMute = toggleMute;
    window.bratTogglePause = togglePause;
    window.bratSetVolume  = setVolume;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            loadTrack(state.index, state.time, true);
            updateUI();
        });
    } else {
        loadTrack(state.index, state.time, true);
        updateUI();
    }
})();
