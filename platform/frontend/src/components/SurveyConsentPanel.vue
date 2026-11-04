<template>
  <section class="survey-panel" aria-labelledby="survey-panel-title">
    <h2 id="survey-panel-title" class="section-title">Surveys</h2>
    <p class="survey-panel__lead">
      Optional short surveys help us improve the platform. They ask about
      features and usage only, never your password, grades, lab flags, or
      sensitive personal information. You can opt in or withdraw at any time.
    </p>

    <div v-if="loading" class="survey-panel__status">Loading survey preferences...</div>

    <template v-else>
      <div class="survey-panel__state" :class="{ 'survey-panel__state--in': optedIn }">
        <span class="survey-panel__badge">{{ optedIn ? 'Opted in' : 'Not opted in' }}</span>
        <span v-if="optedIn && optedInAt" class="survey-panel__meta">
          since {{ formatDate(optedInAt) }}
          <template v-if="consentVersion"> &middot; statement v{{ consentVersion }}</template>
        </span>
        <span v-else class="survey-panel__meta">
          No survey invitations will be sent.
        </span>
      </div>

      <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success-message" role="status">{{ successMessage }}</p>

      <div class="survey-panel__actions">
        <button
          v-if="!optedIn"
          type="button"
          class="btn btn--primary"
          :disabled="saving"
          @click="openStatement(true)"
        >
          Opt in to surveys
        </button>
        <button
          v-else
          type="button"
          class="btn btn--secondary"
          :disabled="saving || withdrawing"
          @click="confirmWithdraw = true"
        >
          Withdraw consent
        </button>
        <button type="button" class="btn btn--secondary" @click="openStatement(false)">
          Read the privacy statement
        </button>
      </div>

      <div v-if="confirmWithdraw" class="survey-panel__confirm" role="alert">
        <p>
          Withdrawing stops future survey invitations. Responses you already sent
          stay in the survey results until their retention period ends; contact
          {{ statement?.contact_email || 'the privacy contact' }} if you want them
          deleted sooner.
        </p>
        <div class="survey-panel__confirm-actions">
          <button
            type="button"
            class="btn btn--danger btn--sm"
            :disabled="withdrawing"
            @click="withdraw"
          >
            {{ withdrawing ? 'Withdrawing...' : 'Yes, withdraw consent' }}
          </button>
          <button
            type="button"
            class="btn btn--secondary btn--sm"
            :disabled="withdrawing"
            @click="confirmWithdraw = false"
          >
            Keep my consent
          </button>
        </div>
      </div>
    </template>

    <div
      v-if="statementOpen"
      class="survey-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="survey-statement-title"
      tabindex="-1"
      @click.self="closeStatement"
      @keydown.esc="closeStatement"
    >
      <div class="survey-modal__card">
        <header class="survey-modal__header">
          <div>
            <h3 id="survey-statement-title">{{ statement?.title || 'Survey privacy statement' }}</h3>
            <p v-if="statement" class="survey-modal__version">
              Version {{ statement.version }} &middot; updated {{ statement.updated }}
            </p>
          </div>
          <button
            type="button"
            class="survey-modal__close"
            aria-label="Close privacy statement"
            @click="closeStatement"
          >
            &times;
          </button>
        </header>

        <div v-if="statement" class="survey-modal__body">
          <p class="survey-modal__summary">{{ statement.summary }}</p>
          <section v-for="(section, index) in statement.sections" :key="index" class="survey-modal__section">
            <h4>{{ section.heading }}</h4>
            <p v-for="(paragraph, pIndex) in section.paragraphs" :key="pIndex">{{ paragraph }}</p>
            <ul v-if="section.bullets && section.bullets.length">
              <li v-for="(bullet, bIndex) in section.bullets" :key="bIndex">{{ bullet }}</li>
            </ul>
          </section>
          <p v-if="statement.note" class="survey-modal__note">{{ statement.note }}</p>
        </div>

        <footer class="survey-modal__footer">
          <button type="button" class="btn btn--secondary" @click="closeStatement">
            {{ pendingOptIn ? 'Cancel' : 'Close' }}
          </button>
          <button
            v-if="pendingOptIn"
            type="button"
            class="btn btn--primary"
            :disabled="saving || !statement"
            @click="confirmOptIn"
          >
            {{ saving ? 'Saving...' : 'I agree — opt me in' }}
          </button>
        </footer>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '../api/axios'

const loading = ref(true)
const saving = ref(false)
const withdrawing = ref(false)
const confirmWithdraw = ref(false)
const optedIn = ref(false)
const optedInAt = ref(null)
const consentVersion = ref(null)
const statement = ref(null)
const statementOpen = ref(false)
const pendingOptIn = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const applyState = (data) => {
  optedIn.value = !!data.opt_in
  optedInAt.value = data.opted_in_at || null
  consentVersion.value = data.consent_version || null
  if (data.statement) statement.value = data.statement
}

const load = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await axios.get('/auth/survey-consent')
    applyState(data)
  } catch (e) {
    errorMessage.value =
      e.response?.data?.detail || 'Could not load your survey preferences.'
  } finally {
    loading.value = false
  }
}

const openStatement = (forOptIn) => {
  pendingOptIn.value = !!forOptIn
  statementOpen.value = true
}

const closeStatement = () => {
  statementOpen.value = false
  pendingOptIn.value = false
}

const confirmOptIn = async () => {
  if (!statement.value) return
  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const { data } = await axios.post('/auth/survey-consent', {
      opt_in: true,
      policy_version: statement.value.version,
    })
    applyState(data)
    successMessage.value = data.message || 'You are opted in to surveys.'
    closeStatement()
  } catch (e) {
    errorMessage.value =
      e.response?.data?.detail || 'Could not save your survey preference.'
  } finally {
    saving.value = false
  }
}

const withdraw = async () => {
  withdrawing.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const { data } = await axios.post('/auth/survey-consent', { opt_in: false })
    applyState(data)
    successMessage.value = data.message || 'You are opted out of surveys.'
    confirmWithdraw.value = false
  } catch (e) {
    errorMessage.value =
      e.response?.data?.detail || 'Could not withdraw your survey consent.'
  } finally {
    withdrawing.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.survey-panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.survey-panel .section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.survey-panel__lead {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.55;
  margin: 0 0 0.85rem;
}

.survey-panel__status {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.survey-panel__state {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.85rem;
}

.survey-panel__badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-tertiary, var(--bg-secondary));
  border: 1px solid var(--border-color);
}

.survey-panel__state--in .survey-panel__badge {
  color: var(--success-text, #0a6b3a);
  background: var(--success-bg, rgba(16, 185, 129, 0.12));
  border-color: color-mix(in srgb, var(--success, #10b981) 45%, var(--border-color));
}

.survey-panel__meta {
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.survey-panel__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.survey-panel__confirm {
  margin: 0.85rem 0 0;
  padding: 0.75rem;
  border-radius: 8px;
  background: var(--warning-bg, rgba(245, 158, 11, 0.12));
  color: var(--text-primary);
  font-size: 0.85rem;
  line-height: 1.5;
}

.survey-panel__confirm p {
  margin: 0 0 0.6rem;
}

.survey-panel__confirm-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.survey-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.65);
}

.survey-modal__card {
  display: flex;
  flex-direction: column;
  width: min(720px, 100%);
  max-height: 90vh;
  background: var(--bg-primary, #ffffff);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.35);
}

.survey-modal__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.survey-modal__header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.15rem;
}

.survey-modal__version {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.survey-modal__close {
  border: 0;
  background: transparent;
  color: var(--text-secondary);
  font-size: 1.6rem;
  line-height: 1;
  cursor: pointer;
  padding: 0 0.25rem;
}

.survey-modal__close:hover {
  color: var(--text-primary);
}

.survey-modal__body {
  overflow-y: auto;
  padding: 1.25rem 1.5rem;
}

.survey-modal__summary {
  margin: 0 0 1rem;
  color: var(--text-primary);
  font-size: 0.92rem;
  line-height: 1.55;
}

.survey-modal__section {
  margin-bottom: 1rem;
}

.survey-modal__section h4 {
  margin: 0 0 0.35rem;
  color: var(--text-primary);
  font-size: 0.92rem;
}

.survey-modal__section p,
.survey-modal__section li {
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.55;
}

.survey-modal__section p {
  margin: 0 0 0.45rem;
}

.survey-modal__section ul {
  margin: 0.25rem 0 0.45rem;
  padding-left: 1.2rem;
}

.survey-modal__note {
  margin: 0;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.5;
}

.survey-modal__footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 640px) {
  .survey-panel__actions,
  .survey-modal__footer {
    flex-direction: column;
  }

  .survey-panel__actions .btn,
  .survey-modal__footer .btn {
    width: 100%;
  }
}
</style>
