<template>
  <div class="celebration-wall" :aria-busy="loading">
    <div v-if="error" class="error-card" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--outline btn--sm" @click="loadWall">Try again</button>
    </div>

    <div v-if="loading" class="wall-loading" role="status" aria-live="polite">
      <span class="wall-loading__ring"><TrophyIcon /></span>
      <p>Warming up the applause...</p>
    </div>

    <template v-else-if="hasData">
      <header class="wall-hero">
        <div class="wall-hero__confetti" aria-hidden="true">
          <span
            v-for="piece in confetti"
            :key="piece.id"
            class="wall-confetti"
            :style="piece.style"
          ></span>
        </div>

        <div class="wall-hero__main">
          <p class="wall-hero__kicker">
            <TrophyIcon />
            The Celebration Wall
          </p>
          <h1>Every win deserves a shout-out.</h1>
          <p class="wall-hero__lede">
            Fresh badges, first bloods, and no-hint clears from across the range.
            Take a bow, then go earn the next one.
          </p>

          <div class="wall-hero__stats">
            <div class="wall-stat">
              <strong>{{ stats.total_awards || 0 }}</strong>
              <span>badges awarded</span>
            </div>
            <div class="wall-stat">
              <strong>{{ stats.unique_earners || 0 }}</strong>
              <span>people celebrated</span>
            </div>
            <div class="wall-stat">
              <strong>{{ stats.awards_this_week || 0 }}</strong>
              <span>this week</span>
            </div>
            <div class="wall-stat">
              <strong>{{ stats.first_bloods || 0 }}</strong>
              <span>first bloods</span>
            </div>
          </div>
        </div>

        <aside v-if="me" class="your-corner">
          <p class="your-corner__kicker">Your corner</p>
          <div class="your-corner__score">
            <strong>{{ me.badge_count || 0 }}</strong>
            <span>{{ me.badge_count === 1 ? 'badge' : 'badges' }}</span>
          </div>
          <p v-if="!me.can_list" class="your-corner__rank your-corner__rank--muted">
            Admin accounts are not listed
          </p>
          <p v-else-if="!me.listed" class="your-corner__rank your-corner__rank--muted">
            Private mode: your wins stay off the wall
          </p>
          <p v-else-if="me.name_mode === 'anonymous'" class="your-corner__rank">
            Your wins appear as Anonymous participant
          </p>
          <p v-else-if="me.badge_count" class="your-corner__rank">
            Your wins are on the wall
          </p>
          <p v-else class="your-corner__rank your-corner__rank--muted">
            Your first badge is waiting
          </p>

          <ul v-if="me.recent.length" class="your-corner__recent">
            <li v-for="win in me.recent.slice(0, 2)" :key="win.id">
              <span aria-hidden="true">{{ win.icon }}</span>
              {{ win.label }}
            </li>
          </ul>

          <label v-if="me.can_list" class="your-corner__privacy">
            <input
              type="checkbox"
              :checked="me.listed"
              :disabled="privacySaving"
              @change="setListing($event)"
            />
            <span>{{ privacySaving ? 'Saving...' : 'Show me on the wall' }}</span>
          </label>

          <label v-if="me.can_list" class="your-corner__name">
            <span>Name on the wall</span>
            <select
              :value="me.name_mode || 'real_name'"
              :disabled="privacySaving"
              @change="setNameMode($event)"
            >
              <option value="real_name">Real name &mdash; {{ me.display_name }}</option>
              <option value="username">Username &mdash; @{{ me.username }}</option>
              <option value="anonymous">Anonymous participant</option>
            </select>
          </label>

          <p v-if="privacyMessage" class="your-corner__privacy-msg">{{ privacyMessage }}</p>

          <router-link to="/profile" class="your-corner__link">Open trophy case</router-link>
        </aside>
      </header>

      <div class="wall-grid">
        <section class="card wall-feed">
          <div class="card__header card__header--split">
            <div>
              <h2 class="card__title">Fresh wins</h2>
              <p class="card__subtitle">Newest celebrations across the range</p>
            </div>
            <span class="live-pill"><span class="live-dot"></span> Live-ish</span>
          </div>

          <ol v-if="recent.length" class="win-list">
            <li
              v-for="win in recent"
              :key="win.id"
              class="win"
              :class="{ 'win--mine': win.is_mine }"
            >
              <span class="win__avatar" aria-hidden="true">
                {{ initials(win.display_name || win.username) }}
              </span>
              <span class="win__body">
                <span class="win__who">
                  <strong>{{ win.display_name || win.username || 'A trainee' }}</strong>
                  <span class="win__verb">earned</span>
                  <span class="win__badge" :class="toneClass(win.achievement_type)">
                    {{ win.label }}
                  </span>
                </span>
                <span class="win__meta">
                  <template v-if="win.lab_name">
                    {{ win.lab_name }}<span class="win__dot">·</span>
                  </template>
                  <template v-if="win.course_code">
                    {{ win.course_code }}<span class="win__dot">·</span>
                  </template>
                  {{ relativeTime(win.awarded_at) }}
                </span>
              </span>
              <span
                class="win__icon"
                :class="toneClass(win.achievement_type)"
                :title="win.description || win.label"
                aria-hidden="true"
              >{{ win.icon }}</span>
            </li>
          </ol>

          <div v-else class="empty-state">
            <TrophyIcon class="empty-state__icon" />
            <p class="empty-state__title">No wins on the wall yet.</p>
            <p class="empty-state__hint">Capture the first flag and start the applause.</p>
          </div>

          <div v-if="recent.length" class="feed-footer">
            <span><b>{{ stats.first_bloods || 0 }}</b> first bloods</span>
            <span><b>{{ stats.clean_sweeps || 0 }}</b> clean sweeps</span>
            <span><b>{{ stats.awards_this_week || 0 }}</b> wins this week</span>
          </div>
        </section>

        <aside class="wall-side">
          <section class="card wall-fame">
            <div class="card__header">
              <div>
                <h2 class="card__title">Spotlight</h2>
                <p class="card__subtitle">Recently celebrated people, not a ranking</p>
              </div>
            </div>

            <ol v-if="spotlight.length" class="fame-list">
              <li
                v-for="person in spotlight"
                :key="person.user_id"
                class="fame-row"
                :class="{ 'fame-row--mine': person.is_mine }"
              >
                <span class="fame-avatar" aria-hidden="true">
                  {{ initials(person.display_name || person.username) }}
                </span>
                <span class="fame-name">
                  {{ person.display_name || person.username }}
                  <small v-if="person.is_mine">you</small>
                  <span class="fame-badge">{{ person.latest_icon }} {{ person.latest_label }}</span>
                </span>
                <span class="fame-time">{{ relativeTime(person.awarded_at) }}</span>
              </li>
            </ol>
            <p v-else class="empty-state empty-state--compact">The spotlight is ready for its first win.</p>
          </section>

          <section class="card wall-nudge">
            <span class="wall-nudge__icon"><FlameIcon /></span>
            <h2>Keep the streak alive</h2>
            <p>
              Finish an exercise without hints, or capture a flag on the first try,
              and your name lands here next.
            </p>
            <router-link to="/exercises" class="btn btn--primary btn--sm">
              Find your next badge
            </router-link>
          </section>
        </aside>
      </div>

      <section class="card wall-gallery">
        <div class="card__header card__header--split">
          <div>
            <h2 class="card__title">Badge gallery</h2>
            <p class="card__subtitle">Every kind of win on the wall</p>
          </div>
          <span class="gallery-count">{{ badges.length }} {{ badges.length === 1 ? 'kind' : 'kinds' }}</span>
        </div>

        <div v-if="badges.length" class="badge-grid">
          <article
            v-for="badge in badges"
            :key="badge.type"
            class="badge-tile"
            :class="toneClass(badge.type)"
          >
            <span class="badge-tile__icon" aria-hidden="true">{{ badge.icon }}</span>
            <div class="badge-tile__body">
              <h3>{{ badge.label }}</h3>
              <p v-if="badge.description" class="badge-tile__desc">{{ badge.description }}</p>
              <p class="badge-tile__stats">
                {{ badge.count }} awarded to
                {{ badge.earners }} {{ badge.earners === 1 ? 'person' : 'people' }}
              </p>
            </div>
          </article>
        </div>
        <p v-else class="empty-state">
          No badges have been awarded yet. The first one is up for grabs.
        </p>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'
import { usePoll } from '../composables/usePoll'
import TrophyIcon from '../components/icons/TrophyIcon.vue'
import FlameIcon from '../components/icons/FlameIcon.vue'

const wall = ref({
  stats: {},
  recent: [],
  spotlight: [],
  badges: [],
  me: null,
})

const loading = ref(true)
const error = ref('')
const privacySaving = ref(false)
const privacyMessage = ref('')

const stats = computed(() => wall.value.stats || {})
const recent = computed(() => wall.value.recent || [])
const spotlight = computed(() => wall.value.spotlight || [])
const badges = computed(() => wall.value.badges || [])
const me = computed(() => wall.value.me)
const hasData = computed(() => Boolean(wall.value.generated_at))

const CONFETTI_COLORS = ['#f59e0b', '#22c55e', '#3b82f6', '#a78bfa', '#06b6d4', '#fb923c']
const confetti = Array.from({ length: 18 }, (_, index) => ({
  id: index,
  style: {
    left: `${(index * 53) % 96}%`,
    background: CONFETTI_COLORS[index % CONFETTI_COLORS.length],
    animationDelay: `${(index % 6) * 0.4}s`,
    animationDuration: `${4 + (index % 5)}s`,
  },
}))

const loadWall = async () => {
  error.value = ''
  try {
    const response = await axios.get('/dashboard/celebrations')
    wall.value = response.data
  } catch {
    error.value = 'We could not load the celebration wall. Check your connection and try again.'
  } finally {
    loading.value = false
  }
}

onMounted(loadWall)
usePoll(() => {
  // Refresh quietly so the wall stays current without a loading flash.
  axios.get('/dashboard/celebrations')
    .then((response) => {
      wall.value = response.data
      error.value = ''
    })
    .catch(() => { /* keep the last good wall */ })
}, 60000)

const setListing = async (event) => {
  const shown = event.target.checked
  privacySaving.value = true
  privacyMessage.value = ''
  try {
    await axios.put('/auth/settings', { show_on_scoreboard: shown })
    if (wall.value.me) {
      wall.value.me.listed = shown
    }
    privacyMessage.value = shown
      ? 'You are back on the wall.'
      : 'You are hidden from the public wall. Your own corner stays private.'
    await loadWall()
  } catch {
    event.target.checked = !shown
    privacyMessage.value = 'Could not update that setting. Please try again.'
  } finally {
    privacySaving.value = false
  }
}

const setNameMode = async (event) => {
  const mode = event.target.value
  privacySaving.value = true
  privacyMessage.value = ''
  try {
    await axios.put('/auth/settings', { scoreboard_name_mode: mode })
    if (wall.value.me) {
      wall.value.me.name_mode = mode
    }
    privacyMessage.value = mode === 'anonymous'
      ? 'Your wins will appear as Anonymous participant.'
      : mode === 'username'
        ? 'Your username will appear on the wall.'
        : 'Your real name will appear on the wall.'
    await loadWall()
  } catch {
    event.target.value = wall.value.me?.name_mode || 'real_name'
    privacyMessage.value = 'Could not update that setting. Please try again.'
  } finally {
    privacySaving.value = false
  }
}

const initials = (name) => {
  const cleaned = String(name || '?').trim()
  if (!cleaned) return '?'
  const parts = cleaned.split(/\s+/).filter(Boolean)
  if (parts.length > 1) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return cleaned.slice(0, 2).toUpperCase()
}

const toneClass = (type) => {
  if (!type) return 'tone--custom'
  if (type.startsWith('custom_')) return 'tone--custom'
  return `tone--${type.replaceAll('_', '-')}`
}

const relativeTime = (iso) => {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''

  const seconds = Math.max(1, Math.floor((Date.now() - date.getTime()) / 1000))
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.celebration-wall {
  max-width: 1120px;
  margin: 0 auto;
  padding: 2rem;
}

/* Hero */
.wall-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 240px;
  gap: 1.5rem;
  align-items: stretch;
  overflow: hidden;
  margin-bottom: 1.25rem;
  padding: 1.8rem;
  border: 1px solid var(--border-color);
  border-radius: 18px;
  background:
    radial-gradient(circle at 8% 0%, rgba(245, 158, 11, 0.2), transparent 42%),
    radial-gradient(circle at 90% 12%, rgba(59, 130, 246, 0.22), transparent 46%),
    radial-gradient(circle at 55% 100%, rgba(34, 197, 94, 0.12), transparent 50%),
    var(--bg-secondary);
}

.wall-hero__main {
  position: relative;
  z-index: 1;
  min-width: 0;
}

.wall-hero__kicker {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin: 0 0 0.35rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--warning);
}

.wall-hero__kicker :deep(svg) {
  width: 16px;
  height: 16px;
}

.wall-hero h1 {
  margin: 0;
  font-size: clamp(1.8rem, 4vw, 2.75rem);
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: var(--text-primary);
}

.wall-hero__lede {
  max-width: 560px;
  margin: 0.55rem 0 1.1rem;
  font-size: 0.92rem;
  color: var(--text-secondary);
}

.wall-hero__stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.6rem;
}

.wall-stat {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.65rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: color-mix(in srgb, var(--bg-primary) 70%, transparent);
}

.wall-stat strong {
  font-size: 1.35rem;
  line-height: 1;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.wall-stat span {
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.wall-hero__confetti {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.wall-confetti {
  position: absolute;
  top: -12px;
  width: 6px;
  height: 11px;
  border-radius: 2px;
  opacity: 0.65;
  animation-name: confetti-drift;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}

@keyframes confetti-drift {
  0% { transform: translateY(-20px) rotate(0deg); opacity: 0; }
  12% { opacity: 0.7; }
  100% { transform: translateY(320px) rotate(360deg); opacity: 0; }
}

/* Personal corner */
.your-corner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: color-mix(in srgb, var(--bg-primary) 78%, transparent);
}

.your-corner__kicker {
  margin: 0;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.your-corner__score {
  display: flex;
  align-items: baseline;
  gap: 0.35rem;
  margin: 0.1rem 0;
}

.your-corner__score strong {
  font-size: 2.1rem;
  line-height: 1;
  color: var(--warning);
}

.your-corner__score span {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.your-corner__rank {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--success);
}

.your-corner__rank--muted {
  color: var(--text-muted);
  font-weight: 500;
}

.your-corner__recent {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  margin: 0.35rem 0 0;
  padding: 0;
  list-style: none;
  font-size: 0.72rem;
  color: var(--text-secondary);
}

.your-corner__privacy {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.5rem;
  font-size: 0.68rem;
  color: var(--text-muted);
  cursor: pointer;
}

.your-corner__privacy input {
  accent-color: var(--accent);
}

.your-corner__name {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.55rem;
  font-size: 0.68rem;
  color: var(--text-muted);
}

.your-corner__name select {
  width: 100%;
  padding: 0.35rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.72rem;
}

.your-corner__privacy-msg {
  margin: 0.15rem 0 0;
  font-size: 0.64rem;
  line-height: 1.35;
  color: var(--success);
}

.your-corner__link {
  margin-top: auto;
  padding-top: 0.55rem;
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
}

.your-corner__link:hover {
  text-decoration: underline;
}

/* Layout */
.wall-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(0, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.wall-side {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.3rem;
}

.card__header {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}

.card__header--split {
  justify-content: space-between;
}

.card__title {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.card__subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.live-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.14);
  animation: live-pulse 2.2s ease-in-out infinite;
}

@keyframes live-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

/* Fresh wins feed */
.win-list {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.win {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.6rem 0.45rem;
  border-radius: 10px;
  transition: background 0.15s ease;
}

.win + .win {
  border-top: 1px solid var(--border-color);
}

.win:hover {
  background: var(--bg-primary);
}

.win--mine {
  background:
    linear-gradient(90deg, color-mix(in srgb, var(--warning) 12%, transparent), transparent 65%);
}

.win--mine:hover {
  background:
    linear-gradient(90deg, color-mix(in srgb, var(--warning) 17%, transparent), transparent 65%);
}

.win__avatar,
.fame-avatar {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-weight: 700;
}

.win__avatar {
  width: 36px;
  height: 36px;
  font-size: 0.72rem;
}

.fame-avatar {
  width: 28px;
  height: 28px;
  font-size: 0.62rem;
}

.win__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
  gap: 0.1rem;
}

.win__who {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.35rem;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.win__who strong {
  color: var(--text-primary);
  font-weight: 650;
}

.win__verb {
  color: var(--text-muted);
}

.win__badge {
  --tone: var(--accent);
  padding: 0.1rem 0.45rem;
  border: 1px solid color-mix(in srgb, var(--tone) 45%, var(--border-color));
  border-radius: 999px;
  background: color-mix(in srgb, var(--tone) 10%, transparent);
  color: var(--tone);
  font-size: 0.7rem;
  font-weight: 700;
}

.win__meta {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.7rem;
  color: var(--text-muted);
}

.win__dot {
  margin: 0 0.35rem;
  opacity: 0.6;
}

.win__icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: 10px;
  background: color-mix(in srgb, var(--tone, var(--accent)) 12%, var(--bg-primary));
  font-size: 1.05rem;
  line-height: 1;
}

.feed-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.9rem;
  padding-top: 0.9rem;
  border-top: 1px solid var(--border-color);
}

.feed-footer span {
  padding: 0.22rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.66rem;
  color: var(--text-muted);
}

.feed-footer b {
  color: var(--text-secondary);
}

/* Wall of fame */
.fame-list {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.fame-row {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.42rem 0.3rem;
  border-radius: 8px;
}

.fame-row--mine {
  background: var(--accent-bg);
}

.fame-name {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.3rem;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-primary);
}

.fame-badge {
  flex-basis: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.68rem;
  font-weight: 500;
  color: var(--text-muted);
}

.fame-time {
  flex-shrink: 0;
  font-size: 0.64rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.fame-name small {
  padding: 0.05rem 0.35rem;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent);
  font-size: 0.58rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* Nudge card */
.wall-nudge {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.4rem;
  background:
    radial-gradient(circle at 100% 0%, rgba(251, 146, 60, 0.14), transparent 60%),
    var(--bg-secondary);
}

.wall-nudge__icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: var(--bg-primary);
  color: #fb923c;
}

.wall-nudge__icon :deep(svg) {
  width: 19px;
  height: 19px;
}

.wall-nudge h2 {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.wall-nudge p {
  margin: 0 0 0.5rem;
  font-size: 0.76rem;
  color: var(--text-secondary);
}

/* Badge gallery */
.wall-gallery {
  margin-bottom: 0.5rem;
}

.gallery-count {
  padding: 0.25rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.66rem;
  font-weight: 600;
  color: var(--text-muted);
}

.badge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.75rem;
}

.badge-tile {
  --tone: var(--accent);
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  padding: 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--tone) 8%, transparent), transparent 58%),
    var(--bg-primary);
}

.badge-tile__icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  border-radius: 12px;
  background: color-mix(in srgb, var(--tone) 14%, var(--bg-secondary));
  border: 1px solid color-mix(in srgb, var(--tone) 30%, var(--border-color));
  font-size: 1.25rem;
  line-height: 1;
}

.badge-tile__body {
  min-width: 0;
}

.badge-tile h3 {
  margin: 0;
  font-size: 0.86rem;
  color: var(--text-primary);
}

.badge-tile__desc {
  margin: 0.15rem 0 0.3rem;
  font-size: 0.7rem;
  line-height: 1.4;
  color: var(--text-secondary);
}

.badge-tile__stats {
  margin: 0;
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--tone);
}

/* Tone palette shared by feed badges and gallery tiles */
.tone--first-blood { --tone: var(--warning); }
.tone--no-hints { --tone: var(--success); }
.tone--perfectionist { --tone: var(--accent); }
.tone--speed-demon { --tone: #f59e0b; }
.tone--clean-sweep { --tone: #a78bfa; }
.tone--streak { --tone: #fb923c; }
.tone--custom { --tone: #14b8a6; }

/* Loading, empty, and error states */
.wall-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.9rem;
  padding: 4rem 1rem;
  color: var(--text-muted);
}

.wall-loading__ring {
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  color: var(--warning);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  box-shadow: 0 0 0 6px var(--bg-primary);
  animation: trophy-bob 1.6s ease-in-out infinite;
}

.wall-loading__ring :deep(svg) {
  width: 30px;
  height: 30px;
}

@keyframes trophy-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 1.5rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}

.empty-state--compact {
  padding: 0.9rem;
}

.empty-state__icon {
  width: 34px;
  height: 34px;
  margin-bottom: 0.35rem;
  color: var(--text-muted);
}

.empty-state__title {
  margin: 0;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state__hint {
  margin: 0;
  font-size: 0.74rem;
  color: var(--text-muted);
}

.error-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--danger);
  border-radius: 10px;
  background: var(--danger-bg);
  color: var(--text-primary);
  font-size: 0.85rem;
}

.error-card p {
  margin: 0;
}

/* Responsive */
@media (max-width: 940px) {
  .wall-hero {
    grid-template-columns: 1fr;
  }

  .your-corner {
    max-width: none;
  }

  .wall-grid {
    grid-template-columns: 1fr;
  }

  .wall-side {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .celebration-wall {
    padding: 1rem;
  }

  .wall-hero {
    padding: 1.25rem;
  }

  .wall-hero__stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .wall-side {
    grid-template-columns: 1fr;
  }

  .win__icon {
    display: none;
  }

  .win__meta {
    white-space: normal;
  }
}

@media (prefers-reduced-motion: reduce) {
  .wall-hero__confetti {
    display: none;
  }

  .live-dot,
  .wall-loading__ring,
  .wall-confetti {
    animation: none;
  }
}
</style>
