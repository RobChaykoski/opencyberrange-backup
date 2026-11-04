<template>
  <div class="profile-page">
    <div class="profile-container">
      <div v-if="loading" class="loading-message">Loading profile information...</div>

      <div v-else-if="user" class="profile-content">
        <!-- Profile hero: avatar, identity, and completion stats -->
        <section class="profile-hero">
          <div class="profile-avatar">
            <div class="profile-avatar__frame" :class="{ 'profile-avatar__frame--empty': !avatarPreview }">
              <img v-if="avatarPreview" :src="avatarPreview" alt="Your profile picture" />
              <span v-else>{{ initials }}</span>
            </div>
            <input
              ref="avatarInput"
              type="file"
              accept="image/png,image/jpeg,image/webp"
              class="avatar-input"
              @change="onAvatarSelected"
            />
            <div class="profile-avatar__actions">
              <button type="button" class="btn btn--secondary btn--sm" :disabled="avatarSaving" @click="chooseAvatar">
                {{ avatarSaving ? 'Saving...' : (avatarPreview ? 'Change photo' : 'Add photo') }}
              </button>
              <button v-if="avatarPreview" type="button" class="btn btn--ghost-danger btn--sm" :disabled="avatarSaving" @click="removeAvatar">
                Remove
              </button>
            </div>
            <p v-if="avatarMessage" :class="avatarError ? 'error-message' : 'success-message'" class="avatar-message">
              {{ avatarMessage }}
            </p>
          </div>

          <div class="profile-hero__identity">
            <p class="profile-hero__eyebrow">OpenCyberRange profile</p>
            <h1 class="profile-hero__name">{{ displayName }}</h1>
            <p class="profile-hero__handle">
              <span>@{{ user.username }}</span>
              <span class="profile-hero__dot">·</span>
              <span>{{ user.email }}</span>
            </p>
            <p v-if="user.organization" class="profile-hero__org">{{ user.organization }}</p>
            <div class="profile-hero__badges">
              <span class="status-badge" :class="roleBadgeClass">{{ roleLabel }}</span>
              <span v-if="user.is_approved" class="status-badge status-badge--approved">Approved</span>
              <span v-else class="status-badge status-badge--pending">Pending approval</span>
              <span v-if="user.created_at" class="profile-hero__joined">Member since {{ formatDateOnly(user.created_at) }}</span>
            </div>
          </div>

          <div class="profile-stats">
            <div class="profile-stat">
              <span class="profile-stat__value">{{ summary ? summary.totals.certificates : '—' }}</span>
              <span class="profile-stat__label">Certificates</span>
            </div>
            <div class="profile-stat">
              <span class="profile-stat__value">
                {{ summary ? summary.totals.labs_completed : '—' }}<small v-if="summary">/{{ summary.totals.labs_total }}</small>
              </span>
              <span class="profile-stat__label">Exercises</span>
            </div>
            <div class="profile-stat">
              <span class="profile-stat__value">{{ summary ? summary.totals.progress_percent : '—' }}<small v-if="summary">%</small></span>
              <span class="profile-stat__label">Complete</span>
            </div>
          </div>
        </section>

        <!-- Certificates and printable transcript -->
        <section class="profile-section transcript-section">
          <div class="transcript-head">
            <div>
              <h2 class="section-title">Certificates &amp; completion</h2>
              <p class="help-text transcript-help">
                Certificates are issued when every visible exercise in a level is complete.
                The PDF includes your certificates, every completed exercise, and course achievements.
              </p>
            </div>
            <button type="button" class="btn btn--primary transcript-download" :disabled="downloadingPdf || summaryLoading" @click="downloadTranscript">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ downloadingPdf ? 'Preparing PDF...' : 'Download PDF' }}
            </button>
          </div>

          <p v-if="pdfMessage" :class="pdfError ? 'error-message' : 'success-message'" class="transcript-message">{{ pdfMessage }}</p>
          <p v-if="summaryError" class="error-message transcript-message">{{ summaryError }}</p>
          <p v-if="summaryLoading && !summary" class="help-text">Loading your completion record...</p>

          <template v-if="summary">
            <div v-if="certificates.length" class="certificate-grid">
              <router-link
                v-for="cert in certificates"
                :key="cert.certificate_id"
                :to="`/certificate/${cert.track_slug}/${cert.level_id}`"
                class="certificate-card"
              >
                <span class="certificate-card__seal" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <circle cx="12" cy="9" r="5"/>
                    <path d="M8.5 13.2 7 21l5-2.6L17 21l-1.5-7.8"/>
                  </svg>
                </span>
                <span class="certificate-card__track" :style="{ color: cert.track_color || 'var(--accent)' }">{{ cert.track_name }}</span>
                <span class="certificate-card__title">Level {{ cert.level_number }}: {{ cert.level_name }}</span>
                <span class="certificate-card__meta">
                  Awarded {{ cert.issued_display }} · {{ cert.exercises_completed }} exercises
                  <template v-if="cert.quiz_score !== null && cert.quiz_score !== undefined"> · Quiz {{ cert.quiz_score }}%</template>
                </span>
                <span class="certificate-card__id">{{ cert.certificate_id }}</span>
              </router-link>
            </div>
            <p v-else class="empty-transcript">
              No certificates yet. Finish every exercise in a level and the certificate appears here.
            </p>

            <div v-if="tracks.length" class="profile-tracks">
              <h3 class="subsection-title">Track progress</h3>
              <div v-for="track in tracks" :key="track.track_slug" class="track-progress">
                <div class="track-progress__head">
                  <span class="track-progress__name">{{ track.track_name }}</span>
                  <span class="track-progress__count">{{ track.completed_labs }} / {{ track.total_labs }} exercises</span>
                </div>
                <div class="track-progress__bar" role="progressbar" :aria-valuenow="track.progress_percent" aria-valuemin="0" aria-valuemax="100">
                  <span :style="{ width: track.progress_percent + '%' }"></span>
                </div>
                <div class="track-progress__levels">
                  <div
                    v-for="level in track.levels"
                    :key="level.id"
                    class="level-card"
                    :class="{
                      'level-card--complete': level.is_complete,
                      'level-card--started': level.completed_labs > 0 && !level.is_complete,
                    }"
                  >
                    <div class="level-card__head">
                      <span class="level-card__number">Level {{ level.level_number }}</span>
                      <span class="level-card__status">{{ levelStatus(level) }}</span>
                    </div>
                    <span class="level-card__name">{{ level.level_name }}</span>
                    <div
                      class="level-card__progress"
                      role="progressbar"
                      :aria-valuenow="levelPercent(level)"
                      aria-valuemin="0"
                      aria-valuemax="100"
                      :aria-label="`${level.level_name}: ${level.completed_labs} of ${level.total_labs} exercises complete`"
                    >
                      <span :style="{ width: levelPercent(level) + '%' }"></span>
                    </div>
                    <div class="level-card__foot">
                      <span>{{ level.completed_labs }} / {{ level.total_labs }} exercises</span>
                      <span v-if="level.certificate_id" class="level-card__cert">Certificate</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <details v-if="completions.length" class="completion-details">
              <summary>Completion details ({{ completions.length }})</summary>
              <div class="completion-table-wrap">
                <table class="completion-table" aria-label="Completed exercises">
                  <thead>
                    <tr>
                      <th scope="col">Exercise</th>
                      <th scope="col">Track</th>
                      <th scope="col">Completed</th>
                      <th scope="col">Attempts</th>
                      <th scope="col">Hints</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in completions" :key="item.lab_id">
                      <td>
                        <span class="completion-table__lab">{{ item.lab_name }}</span>
                        <span class="completion-table__level">Level {{ item.level_number }}: {{ item.level_name }}</span>
                      </td>
                      <td>{{ item.track_name }}</td>
                      <td>{{ formatCompletionDate(item.completed_at) }}</td>
                      <td>{{ item.attempts }}</td>
                      <td>{{ item.hints_used }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <div v-if="achievements.length" class="achievement-strip">
              <h3 class="subsection-title">Course achievements</h3>
              <div class="achievement-list">
                <span
                  v-for="achievement in achievements"
                  :key="achievement.id"
                  class="achievement-chip"
                  :title="achievement.description || achievement.label"
                >
                  <span class="achievement-chip__icon" aria-hidden="true">{{ achievement.icon }}</span>
                  {{ achievement.label }}
                </span>
              </div>
            </div>
          </template>
        </section>
        <div class="profile-section">
          <h2 class="section-title">Personal Information</h2>
          <p class="help-text" style="margin: -0.5rem 0 1rem;">
            Your first and last name are printed on completion certificates.
            If you leave both blank, your username is used instead.
          </p>

          <form class="name-form" @submit.prevent="saveName">
            <div class="name-grid">
              <div class="form-group">
                <label for="firstName">First name</label>
                <input
                  id="firstName"
                  v-model="nameForm.first_name"
                  type="text"
                  maxlength="80"
                  class="form-input"
                  placeholder="e.g. Alex"
                  autocomplete="given-name"
                />
              </div>
              <div class="form-group">
                <label for="lastName">Last name</label>
                <input
                  id="lastName"
                  v-model="nameForm.last_name"
                  type="text"
                  maxlength="80"
                  class="form-input"
                  placeholder="e.g. Morgan"
                  autocomplete="family-name"
                />
              </div>
              <div class="form-group">
                <label for="organization">Organization <span class="help-text">(optional)</span></label>
                <input
                  id="organization"
                  v-model="nameForm.organization"
                  type="text"
                  maxlength="120"
                  class="form-input"
                  placeholder="e.g. University or team"
                  autocomplete="organization"
                />
              </div>
            </div>

            <p class="help-text certificate-preview">
              Certificates will show:
              <strong>{{ certificateName }}</strong>
            </p>
            <p v-if="nameMessage" :class="nameError ? 'error-message' : 'success-message'" style="margin-top: 0.75rem;">
              {{ nameMessage }}
            </p>
            <button type="submit" :disabled="nameSaving" class="btn btn--primary">
              {{ nameSaving ? 'Saving...' : 'Save name' }}
            </button>
          </form>
        </div>

        <!-- Account Information Section -->
        <div class="profile-section">
          <h2 class="section-title">Account Information</h2>
          
          <div class="info-grid">
            <div class="info-item">
              <label class="info-label">Username</label>
              <div class="info-value">{{ user.username }}</div>
            </div>

            <div class="info-item">
              <label class="info-label">Email</label>
              <div class="info-value">{{ user.email }}</div>
            </div>

            <div class="info-item">
              <label class="info-label">Account Status</label>
              <div class="info-value">
                <span v-if="user.is_approved" class="status-badge status-badge--approved">Approved</span>
                <span v-else class="status-badge status-badge--pending">Pending Approval</span>
              </div>
            </div>

            <div class="info-item">
              <label class="info-label">Account Active</label>
              <div class="info-value">
                <span v-if="user.is_active !== false" class="status-badge status-badge--active">Active</span>
                <span v-else class="status-badge status-badge--inactive">Inactive</span>
              </div>
            </div>

            <div class="info-item" v-if="user.created_at">
              <label class="info-label">Registration Date</label>
              <div class="info-value">{{ formatDate(user.created_at) }}</div>
            </div>

            <div class="info-item">
              <label class="info-label">VPN Registered</label>
              <div class="info-value">
                <!-- Use shared composable logic - same as Dashboard -->
                <span v-if="isVpnRegistered()" class="status-badge status-badge--vpn">Yes</span>
                <span v-else class="status-badge status-badge--no-vpn">No</span>
              </div>
            </div>

            <div class="info-item">
              <label class="info-label">Role</label>
              <div class="info-value">
                <span v-if="user.role === 'admin'" class="status-badge status-badge--admin">Admin</span>
                <span v-else-if="user.role === 'instructor'" class="status-badge status-badge--instructor">Instructor</span>
                <span v-else class="status-badge status-badge--user">Student</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Exercise Studio LLM connections (instructor/admin, editions that ship Studio) -->
        <div class="profile-section" v-if="isInstructor && exerciseAuthoring">
          <h2 class="section-title">Exercise Studio</h2>
          <label class="info-label">LLM provider connections</label>
          <p class="help-text" style="margin: 0.35rem 0 0.85rem;">
            Connect a model to generate exercises. Add more than one and pick a default; the one marked Default is used unless you choose another at generation time. Keys are stored encrypted and never shown again.
          </p>

          <!-- Saved profiles -->
          <div v-if="llm.profiles.length" class="llm-list">
            <div v-for="p in llm.profiles" :key="p.id" class="llm-row">
              <div class="llm-row__main">
                <span class="llm-row__label">{{ p.label }}</span>
                <span class="llm-row__meta">{{ providerLabel(p.provider) }} : {{ p.model || 'default model' }}</span>
                <span v-if="p.base_url" class="llm-row__meta llm-row__url">{{ p.base_url }}</span>
              </div>
              <div class="llm-row__actions">
                <span v-if="p.is_default" class="status-badge status-badge--approved">Default</span>
                <button v-else class="btn btn--secondary btn--sm" @click="makeDefault(p.id)">Make default</button>
                <button class="btn btn--ghost-danger btn--sm" @click="removeProfile(p.id)">Remove</button>
              </div>
            </div>
          </div>
          <p v-else class="help-text" style="margin: 0 0 0.85rem;">No connections yet. Add one below.</p>

          <!-- Add a connection -->
          <div class="llm-add">
            <div class="llm-field">
              <label class="info-label">Provider</label>
              <select aria-label="Provider" v-model="llm.form.provider" class="form-input" @change="onProviderChange">
                <option v-for="c in llm.catalog" :key="c.id" :value="c.id">{{ c.label }}</option>
              </select>
            </div>
            <div class="llm-field" v-if="currentSpec && currentSpec.fields.includes('base_url')">
              <label class="info-label">Endpoint URL</label>
              <input aria-label="Endpoint URL" v-model="llm.form.base_url" type="text" class="form-input" :placeholder="currentSpec.base_url_hint || 'https://...'" />
            </div>
            <div class="llm-field" v-if="currentSpec && currentSpec.fields.includes('api_key')">
              <label class="info-label">API key <span v-if="!currentSpec.needs_key" class="help-text">(optional)</span></label>
              <input v-model="llm.form.api_key" type="password" class="form-input" :placeholder="currentSpec.key_hint || ''" autocomplete="off" />
            </div>
            <div class="llm-field" v-if="currentSpec && currentSpec.fields.includes('model')">
              <label class="info-label">Model</label>
              <input aria-label="Model" v-if="!(currentSpec.models && currentSpec.models.length)" v-model="llm.form.model" type="text" class="form-input" :placeholder="currentSpec.model_hint || currentSpec.default_model || ''" />
              <select v-else v-model="llm.form.model" class="form-input">
                <option v-for="m in currentSpec.models" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="llm-field">
              <label class="info-label">Label <span class="help-text">(optional)</span></label>
              <input v-model="llm.form.label" type="text" class="form-input" placeholder="e.g. My Provider, Lab Ollama" />
            </div>
            <div class="llm-actions">
              <button class="btn btn--secondary" :disabled="llm.testing || llm.saving" @click="testConnection">
                {{ llm.testing ? 'Testing...' : 'Test connection' }}
              </button>
              <button class="btn btn--primary" :disabled="llm.saving" @click="saveProfile">
                {{ llm.saving ? 'Saving...' : 'Save connection' }}
              </button>
            </div>
            <p v-if="llm.testMsg" :class="llm.testOk ? 'success-message' : 'error-message'" style="margin-top: 0.5rem;">{{ llm.testMsg }}</p>
            <p v-if="llm.msg" :class="llm.err ? 'error-message' : 'success-message'" style="margin-top: 0.5rem;">{{ llm.msg }}</p>
          </div>
        </div>

        <!-- Course Enrollment Section -->
        <div class="profile-section">
          <h2 class="section-title">Course Enrollment</h2>

          <div class="join-course-form">
            <label class="info-label">Join a Course</label>
            <div class="join-row">
              <input
                v-model="inviteCode"
                type="text"
                placeholder="Enter invite code"
                class="form-input"
                @keyup.enter="joinCourse"
              />
              <button @click="joinCourse" :disabled="!inviteCode.trim() || joiningCourse" class="btn btn--primary">
                {{ joiningCourse ? 'Joining...' : 'Join' }}
              </button>
            </div>
            <p v-if="joinMessage" :class="joinError ? 'error-message' : 'success-message'" style="margin-top: 0.75rem;">{{ joinMessage }}</p>
          </div>

          <div v-if="enrolledCourses.length > 0" class="enrolled-courses">
            <h4 class="enrolled-courses__title">My Courses</h4>
            <div class="enrolled-courses__list">
              <router-link
                v-for="c in enrolledCourses"
                :key="c.id"
                :to="'/courses/' + c.id"
                class="enrolled-course-card"
              >
                <div class="enrolled-course-card__info">
                  <span class="enrolled-course-card__name">{{ c.name }}</span>
                  <span class="enrolled-course-card__code">{{ c.code }} &mdash; {{ c.semester }}</span>
                </div>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="enrolled-course-card__arrow">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </router-link>
            </div>
          </div>
          <p v-else class="empty-courses">Not enrolled in any courses yet.</p>
        </div>

        <!-- Two-Factor Authentication (TOTP) -->
        <div class="profile-section">
          <h2 class="section-title">Two-Factor Authentication (TOTP)</h2>
          <p class="help-text" style="margin: 0 0 0.85rem;">
            Add a second factor using an authenticator app (Google Authenticator, Authy, 1Password, etc.).
          </p>

          <div v-if="user.mfa_enabled" class="info-grid">
            <div class="info-item">
              <label class="info-label">Status</label>
              <div class="info-value"><span class="status-badge status-badge--approved">Enabled</span></div>
            </div>
          </div>

          <div v-if="!user.mfa_enabled && !mfa.enrolling" class="join-row" style="margin-top: 0.5rem;">
            <button class="btn btn--primary" :disabled="mfa.loading" @click="startMfaEnroll">
              {{ mfa.loading ? 'Starting...' : 'Enable MFA' }}
            </button>
            <p v-if="mfa.error" class="error-message" style="margin-top: 0.5rem;">{{ mfa.error }}</p>
          </div>

          <div v-if="!user.mfa_enabled && mfa.enrolling" style="margin-top: 0.75rem;">
            <p class="help-text">Scan the QR code with your authenticator app, or enter the secret manually:</p>
            <div v-if="mfa.qr" class="mfa-qr-wrap">
              <img :src="mfa.qr" alt="QR code to add this account to an authenticator app" class="mfa-qr" />
              <p class="help-text">Works with Google Authenticator, 1Password, Authy, and similar apps.</p>
            </div>
            <details class="mfa-manual">
              <summary>Can't scan? Enter the secret manually</summary>
              <div class="info-item" style="margin: 0.5rem 0;">
                <label class="info-label">Secret</label>
                <div class="info-value"><code>{{ mfa.secret }}</code></div>
              </div>
              <div class="info-item" style="margin: 0.5rem 0;">
                <label class="info-label">Provisioning URI</label>
                <div class="info-value" style="word-break: break-all;"><code>{{ mfa.uri }}</code></div>
              </div>
            </details>
            <div class="join-row" style="margin-top: 0.75rem;">
              <input v-model="mfa.code" type="text" inputmode="numeric" placeholder="6-digit code" class="form-input" @keyup.enter="verifyMfa" />
              <button class="btn btn--primary" :disabled="mfa.loading || !mfa.code.trim()" @click="verifyMfa">
                {{ mfa.loading ? 'Verifying...' : 'Verify & Enable' }}
              </button>
              <button class="btn btn--secondary" @click="cancelMfaEnroll">Cancel</button>
            </div>
            <p v-if="mfa.error" class="error-message" style="margin-top: 0.5rem;">{{ mfa.error }}</p>
            <p v-if="mfa.success" class="success-message" style="margin-top: 0.5rem;">{{ mfa.success }}</p>
          </div>

          <div v-if="user.mfa_enabled" style="margin-top: 0.75rem;">
            <div class="join-row" style="flex-wrap: wrap;">
              <input v-model="mfa.password" type="password" placeholder="Current password" class="form-input" />
              <input v-model="mfa.code" type="text" inputmode="numeric" placeholder="6-digit code" class="form-input" />
              <button class="btn btn--ghost-danger" :disabled="mfa.loading" @click="disableMfa">
                {{ mfa.loading ? 'Disabling...' : 'Disable MFA' }}
              </button>
            </div>
            <p v-if="mfa.error" class="error-message" style="margin-top: 0.5rem;">{{ mfa.error }}</p>
            <p v-if="mfa.success" class="success-message" style="margin-top: 0.5rem;">{{ mfa.success }}</p>
          </div>
        </div>

        <!-- Password Change Section -->
        <div class="profile-section">
          <h2 class="section-title">Change Password</h2>
          
          <form @submit.prevent="changePassword" class="password-form">
            <div class="form-group">
              <label for="currentPassword">Current Password</label>
              <div class="input-wrapper">
                <input
                  id="currentPassword"
                  v-model="passwordForm.currentPassword"
                  :type="showCurrentPassword ? 'text' : 'password'"
                  placeholder="Enter current password"
                  class="form-input"
                  :class="{ 'error': passwordErrors.currentPassword }"
                  required
                />
                <button
                  type="button"
                  @click="showCurrentPassword = !showCurrentPassword"
                  class="password-toggle"
                >
                  <svg v-if="showCurrentPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <p v-if="passwordErrors.currentPassword" class="error-text">{{ passwordErrors.currentPassword }}</p>
            </div>

            <div class="form-group">
              <label for="newPassword">New Password</label>
              <div class="input-wrapper">
                <input
                  id="newPassword"
                  v-model="passwordForm.newPassword"
                  :type="showNewPassword ? 'text' : 'password'"
                  placeholder="Enter new password"
                  class="form-input"
                  :class="{ 'error': passwordErrors.newPassword }"
                  required
                  @blur="validateNewPassword"
                />
                <button
                  type="button"
                  @click="showNewPassword = !showNewPassword"
                  class="password-toggle"
                >
                  <svg v-if="showNewPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <p v-if="passwordErrors.newPassword" class="error-text">{{ passwordErrors.newPassword }}</p>
              <p v-else-if="passwordForm.newPassword && !passwordErrors.newPassword" class="help-text">
                Password must be at least 8 characters and contain uppercase, lowercase, and a number.
              </p>
            </div>

            <div class="form-group">
              <label for="confirmPassword">Confirm New Password</label>
              <div class="input-wrapper">
                <input
                  id="confirmPassword"
                  v-model="passwordForm.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="Confirm new password"
                  class="form-input"
                  :class="{ 'error': passwordErrors.confirmPassword }"
                  required
                  @blur="validateConfirmPassword"
                />
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="password-toggle"
                >
                  <svg v-if="showConfirmPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <p v-if="passwordErrors.confirmPassword" class="error-text">{{ passwordErrors.confirmPassword }}</p>
            </div>

            <p v-if="passwordErrorMessage" class="error-message">{{ passwordErrorMessage }}</p>
            <p v-if="passwordSuccessMessage" class="success-message">{{ passwordSuccessMessage }}</p>

            <button type="submit" :disabled="passwordLoading" class="btn btn--primary">
              <span v-if="passwordLoading">Changing Password...</span>
              <span v-else>Change Password</span>
            </button>
          </form>
        </div>

        <SurveyConsentPanel />
        <PrivacyDataPanel :mfa-enabled="!!user.mfa_enabled" />
      </div>

      <div v-else class="error-message">Failed to load profile information</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../api/axios'
import { useVpnStatus } from '../composables/useVpnStatus'
import { usePoll } from '../composables/usePoll'
import { useModules } from '../composables/useModules'
import PrivacyDataPanel from '../components/PrivacyDataPanel.vue'
import SurveyConsentPanel from '../components/SurveyConsentPanel.vue'
import { getUserTimeZone } from '../utils/timezone'

const route = useRoute()
const router = useRouter()
const { exerciseAuthoring, fetchModules } = useModules()
const user = ref(null)
const { vpnStatus, fetchVpnStatus, isVpnRegistered } = useVpnStatus()

const mfa = reactive({
  loading: false,
  enrolling: false,
  secret: '',
  uri: '',
  qr: '',
  code: '',
  password: '',
  error: '',
  success: '',
})
const loading = ref(true)

// Completion record (certificates, track progress, achievements) for the hero
// and transcript sections. Loaded separately from /auth/me so the account
// forms render immediately even when that aggregate query is slow.
const summary = ref(null)
const summaryLoading = ref(true)
const summaryError = ref('')
const downloadingPdf = ref(false)
const pdfMessage = ref('')
const pdfError = ref(false)

// Profile avatar. Images are resized in the browser and stored on the user row
// as a data URL by /auth/settings, so no upload volume is required.
const avatarInput = ref(null)
const avatarSaving = ref(false)
const avatarMessage = ref('')
const avatarError = ref(false)

const displayName = computed(() => {
  if (!user.value) return ''
  const parts = [user.value.first_name, user.value.last_name].filter(part => part && part.trim())
  return parts.length ? parts.join(' ') : user.value.username
})

const initials = computed(() => {
  const source = displayName.value || user.value?.username || '?'
  const words = source.trim().split(/\s+/).filter(Boolean)
  if (!words.length) return '?'
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase()
  return (words[0][0] + words[words.length - 1][0]).toUpperCase()
})

const levelPercent = (level) => {
  const total = Number(level?.total_labs) || 0
  const done = Number(level?.completed_labs) || 0
  return total ? Math.round((done / total) * 100) : 0
}

const levelStatus = (level) => {
  if (level?.is_complete) return 'Complete'
  return Number(level?.completed_labs) > 0 ? 'In progress' : 'Not started'
}

const avatarPreview = computed(() => user.value?.avatar_data || '')

const roleLabel = computed(() => {
  if (user.value?.role === 'admin') return 'Admin'
  if (user.value?.role === 'instructor') return 'Instructor'
  return 'Student'
})

const roleBadgeClass = computed(() => ({
  'status-badge--admin': user.value?.role === 'admin',
  'status-badge--instructor': user.value?.role === 'instructor',
  'status-badge--user': !['admin', 'instructor'].includes(user.value?.role),
}))

const certificates = computed(() => summary.value?.certificates || [])
const tracks = computed(() => summary.value?.tracks || [])
const completions = computed(() => summary.value?.completions || [])
const achievements = computed(() => summary.value?.achievements || [])

// Personal information shown on certificates
const nameForm = reactive({ first_name: '', last_name: '', organization: '' })
const nameSaving = ref(false)
const nameMessage = ref('')
const nameError = ref(false)

const certificateName = computed(() => {
  const parts = [nameForm.first_name.trim(), nameForm.last_name.trim()].filter(Boolean)
  return parts.length ? parts.join(' ') : (user.value?.username || '')
})

const saveName = async () => {
  if (nameSaving.value) return
  nameSaving.value = true
  nameMessage.value = ''
  nameError.value = false
  // Empty strings are deliberate: the settings endpoint treats null as
  // "leave unchanged", while "" clears a previously saved name.
  const payload = {
    first_name: nameForm.first_name.trim(),
    last_name: nameForm.last_name.trim(),
    organization: nameForm.organization.trim(),
  }
  try {
    await axios.put('/auth/settings', payload)
    if (user.value) {
      user.value.first_name = payload.first_name || null
      user.value.last_name = payload.last_name || null
      user.value.organization = payload.organization || null
    }
    // Keep the cached login object in sync so other views see the new name.
    const cached = JSON.parse(localStorage.getItem('user') || '{}')
    cached.first_name = payload.first_name || null
    cached.last_name = payload.last_name || null
    cached.organization = payload.organization || null
    localStorage.setItem('user', JSON.stringify(cached))
    nameMessage.value = (payload.first_name || payload.last_name)
      ? 'Name saved. It will appear on your certificates.'
      : 'Name cleared. Certificates will use your username.'
    if (window.__updateAuthState) window.__updateAuthState()
  } catch (e) {
    nameError.value = true
    nameMessage.value = e.response?.data?.detail || 'Failed to save your name. Please try again.'
  } finally {
    nameSaving.value = false
  }
}

function responseMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail) && detail.length) return detail[0]?.msg || fallback
  return fallback
}

function chooseAvatar() {
  avatarInput.value?.click()
}

function resizeAvatar(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('Could not read that image.'))
    reader.onload = () => {
      const image = new Image()
      image.onerror = () => reject(new Error('That file is not a readable image.'))
      image.onload = () => {
        const maxSize = 320
        const scale = Math.min(1, maxSize / Math.max(image.width, image.height))
        const width = Math.max(1, Math.round(image.width * scale))
        const height = Math.max(1, Math.round(image.height * scale))
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const context = canvas.getContext('2d')
        // JPEG has no alpha; fill white so transparent PNGs do not turn black.
        context.fillStyle = '#ffffff'
        context.fillRect(0, 0, width, height)
        context.drawImage(image, 0, 0, width, height)
        resolve(canvas.toDataURL('image/jpeg', 0.86))
      }
      image.src = reader.result
    }
    reader.readAsDataURL(file)
  })
}

async function onAvatarSelected(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  if (!/^image\/(png|jpeg|webp)$/.test(file.type)) {
    avatarError.value = true
    avatarMessage.value = 'Choose a PNG, JPEG, or WebP image.'
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    avatarError.value = true
    avatarMessage.value = 'Choose an image smaller than 10 MB.'
    return
  }

  avatarSaving.value = true
  avatarMessage.value = ''
  avatarError.value = false
  try {
    const dataUrl = await resizeAvatar(file)
    await axios.put('/auth/settings', { avatar_data: dataUrl })
    if (user.value) user.value.avatar_data = dataUrl
    if (summary.value?.user) summary.value.user.avatar_data = dataUrl
    avatarMessage.value = 'Profile photo updated.'
  } catch (error) {
    avatarError.value = true
    avatarMessage.value = responseMessage(error, 'Could not save your profile photo.')
  } finally {
    avatarSaving.value = false
  }
}

async function removeAvatar() {
  if (avatarSaving.value) return
  avatarSaving.value = true
  avatarMessage.value = ''
  avatarError.value = false
  try {
    await axios.put('/auth/settings', { avatar_data: '' })
    if (user.value) user.value.avatar_data = null
    if (summary.value?.user) summary.value.user.avatar_data = null
    avatarMessage.value = 'Profile photo removed.'
  } catch (error) {
    avatarError.value = true
    avatarMessage.value = responseMessage(error, 'Could not remove your profile photo.')
  } finally {
    avatarSaving.value = false
  }
}

async function fetchSummary() {
  summaryLoading.value = true
  summaryError.value = ''
  try {
    const { data } = await axios.get('/profile/summary')
    summary.value = data
    if (user.value && data.user) {
      if (data.user.avatar_data) user.value.avatar_data = data.user.avatar_data
      user.value.organization = data.user.organization
    }
  } catch (error) {
    summaryError.value = responseMessage(error, 'Could not load your completion record.')
  } finally {
    summaryLoading.value = false
  }
}

async function downloadTranscript() {
  if (downloadingPdf.value) return
  downloadingPdf.value = true
  pdfMessage.value = ''
  pdfError.value = false
  try {
    const response = await axios.get('/profile/transcript.pdf', { responseType: 'blob' })
    const blob = response.data instanceof Blob
      ? response.data
      : new Blob([response.data], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `OpenCyberRange-Transcript-${user.value?.username || 'profile'}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
    pdfMessage.value = 'Your transcript PDF was downloaded.'
  } catch (error) {
    pdfError.value = true
    pdfMessage.value = responseMessage(error, 'Could not generate the transcript PDF.')
  } finally {
    downloadingPdf.value = false
  }
}

const formatDateOnly = (dateStr) => {
  if (!dateStr) return '—'
  const value = dateStr.endsWith('Z') || dateStr.includes('+') ? dateStr : dateStr + 'Z'
  return new Date(value).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

const formatCompletionDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

// Exercise Studio LLM connections (instructor/admin)
const isInstructor = computed(() => ['instructor', 'admin'].includes(user.value?.role))
const llm = reactive({
  profiles: [], catalog: [],
  form: { provider: 'custom', base_url: '', api_key: '', model: '', label: '' },
  saving: false, testing: false, msg: '', err: false, testMsg: '', testOk: false,
})
const currentSpec = computed(() => llm.catalog.find(c => c.id === llm.form.provider) || null)
function providerLabel(id) { const c = llm.catalog.find(x => x.id === id); return c ? c.label.split(' (')[0] : id }
function onProviderChange() {
  const s = currentSpec.value
  llm.form.base_url = s?.default_base_url || ''
  llm.form.api_key = ''
  llm.form.model = s?.default_model || (s?.models && s.models[0]) || ''
  llm.testMsg = ''; llm.msg = ''
}
async function loadStudioLlm() {
  // Exercise Studio is not in every edition; without it these routes 404 and
  // the LLM provider panel is dead controls.
  if (!exerciseAuthoring.value) { llm.profiles = []; llm.catalog = []; return }
  try {
    const r = await axios.get('/studio/providers')
    llm.profiles = r.data.profiles || []
    llm.catalog = r.data.catalog || []
    if (!currentSpec.value && llm.catalog.length) llm.form.provider = llm.catalog[0].id
    onProviderChange()
  } catch { llm.profiles = []; llm.catalog = [] }
}
function _formPayload() {
  return {
    provider: llm.form.provider,
    label: llm.form.label.trim() || null,
    base_url: llm.form.base_url.trim() || null,
    model: llm.form.model.trim() || null,
    api_key: llm.form.api_key.trim() || null,
  }
}
async function testConnection() {
  llm.testing = true; llm.testMsg = ''; llm.msg = ''
  try {
    const r = await axios.post('/studio/providers/test', _formPayload())
    llm.testOk = !!r.data.ok
    llm.testMsg = (r.data.ok ? 'OK: ' : 'Failed: ') + (r.data.detail || '')
      + (r.data.models && r.data.models.length ? ' (' + r.data.models.slice(0, 8).join(', ') + ')' : '')
  } catch (e) {
    llm.testOk = false; llm.testMsg = e.response?.data?.detail || 'Could not reach the test endpoint.'
  } finally { llm.testing = false }
}
async function saveProfile() {
  llm.saving = true; llm.msg = ''
  try {
    await axios.post('/studio/providers', { ..._formPayload(), make_default: llm.profiles.length === 0 })
    llm.form.api_key = ''; llm.form.label = ''
    llm.msg = 'Connection saved.'; llm.err = false; llm.testMsg = ''
    await loadStudioLlm()
  } catch (e) {
    llm.msg = e.response?.data?.detail || 'Could not save the connection.'; llm.err = true
  } finally { llm.saving = false }
}
async function makeDefault(id) {
  try { const r = await axios.post(`/studio/providers/${id}/default`); llm.profiles = r.data.profiles || llm.profiles }
  catch (e) { llm.msg = e.response?.data?.detail || 'Could not set default.'; llm.err = true }
}
async function removeProfile(id) {
  try { const r = await axios.delete(`/studio/providers/${id}`); llm.profiles = r.data.profiles || [] }
  catch (e) { llm.msg = e.response?.data?.detail || 'Could not remove the connection.'; llm.err = true }
}

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordErrors = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// Course enrollment
const inviteCode = ref('')
const joiningCourse = ref(false)
const joinMessage = ref('')
const joinError = ref(false)
const enrolledCourses = ref([])

const fetchEnrolledCourses = async () => {
  try {
    const res = await axios.get('/courses/')
    enrolledCourses.value = res.data.courses || []
  } catch (e) {
    console.error('Failed to fetch courses:', e)
  }
}

const joinCourse = async () => {
  if (!inviteCode.value.trim() || joiningCourse.value) return
  joiningCourse.value = true
  joinMessage.value = ''
  joinError.value = false
  try {
    const res = await axios.post('/courses/join', { invite_code: inviteCode.value.trim() })
    joinMessage.value = res.data.message || 'Successfully enrolled!'
    joinError.value = false
    inviteCode.value = ''
    fetchEnrolledCourses()
  } catch (e) {
    joinMessage.value = e.response?.data?.detail || 'Failed to join course'
    joinError.value = true
  } finally {
    joiningCourse.value = false
  }
}

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const passwordLoading = ref(false)
const passwordErrorMessage = ref('')
const passwordSuccessMessage = ref('')

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr.endsWith('Z') || dateStr.includes('+') ? dateStr : dateStr + 'Z')
  return d.toLocaleString('en-US', { timeZone: getUserTimeZone() })
}

const validateNewPassword = () => {
  passwordErrors.newPassword = ''
  if (!passwordForm.newPassword) return
  
  if (passwordForm.newPassword.length < 8) {
    passwordErrors.newPassword = 'Password must be at least 8 characters'
    return
  }
  if (!/[A-Z]/.test(passwordForm.newPassword)) {
    passwordErrors.newPassword = 'Password must contain at least one uppercase letter'
    return
  }
  if (!/[a-z]/.test(passwordForm.newPassword)) {
    passwordErrors.newPassword = 'Password must contain at least one lowercase letter'
    return
  }
  if (!/[0-9]/.test(passwordForm.newPassword)) {
    passwordErrors.newPassword = 'Password must contain at least one number'
    return
  }
}

const validateConfirmPassword = () => {
  passwordErrors.confirmPassword = ''
  if (!passwordForm.confirmPassword) return
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = 'Passwords do not match'
  }
}

const changePassword = async () => {
  passwordErrorMessage.value = ''
  passwordSuccessMessage.value = ''
  
  // Validate
  validateNewPassword()
  validateConfirmPassword()
  
  if (passwordErrors.newPassword || passwordErrors.confirmPassword) {
    return
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordErrorMessage.value = 'Passwords do not match'
    return
  }
  
  passwordLoading.value = true
  
  try {
    await axios.post('/auth/change-password', {
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword,
      confirm_password: passwordForm.confirmPassword
    })
    
    passwordSuccessMessage.value = 'Password changed successfully! Please sign in again.'
    
    // Clear form
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    
    // The backend revokes every outstanding token after a password change.
    // Drop the invalid local session and return to the login page.
    localStorage.removeItem('token')
    localStorage.removeItem('user')

    // Trigger App.vue reactivity update
    if (window.__updateAuthState) {
      window.__updateAuthState()
    }

    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error) {
    if (error.response?.data?.detail) {
      passwordErrorMessage.value = error.response.data.detail
    } else {
      passwordErrorMessage.value = 'Failed to change password. Please try again.'
    }
  } finally {
    passwordLoading.value = false
  }
}

// fetchVpnStatus is now provided by useVpnStatus composable

const startMfaEnroll = async () => {
  mfa.loading = true
  mfa.error = ''
  mfa.success = ''
  try {
    const r = await axios.post('/auth/mfa/enroll')
    mfa.secret = r.data.secret
    mfa.uri = r.data.provisioning_uri
    mfa.qr = r.data.qr_data_url || ''
    mfa.enrolling = true
  } catch (e) {
    mfa.error = e.response?.data?.detail || 'Failed to start MFA enrollment'
  } finally {
    mfa.loading = false
  }
}

const cancelMfaEnroll = () => {
  mfa.enrolling = false
  mfa.secret = ''
  mfa.uri = ''
  mfa.qr = ''
  mfa.code = ''
  mfa.error = ''
}

const verifyMfa = async () => {
  mfa.loading = true
  mfa.error = ''
  mfa.success = ''
  try {
    const response = await axios.post('/auth/mfa/verify', { code: mfa.code.trim() })
    if (user.value) user.value.mfa_enabled = response.data?.mfa_enabled !== false
    mfa.success = 'MFA enabled successfully.'
    mfa.enrolling = false
    mfa.qr = ''
    mfa.code = ''
    await fetchUserInfo()
  } catch (e) {
    mfa.error = e.response?.data?.detail || 'Invalid MFA code'
  } finally {
    mfa.loading = false
  }
}

const disableMfa = async () => {
  mfa.loading = true
  mfa.error = ''
  mfa.success = ''
  try {
    const response = await axios.post('/auth/mfa/disable', { password: mfa.password, code: mfa.code.trim() })
    if (user.value) user.value.mfa_enabled = response.data?.mfa_enabled === true
    mfa.success = 'MFA disabled.'
    mfa.password = ''
    mfa.code = ''
    await fetchUserInfo()
  } catch (e) {
    mfa.error = e.response?.data?.detail || 'Failed to disable MFA'
  } finally {
    mfa.loading = false
  }
}

const fetchUserInfo = async () => {
  try {
    const [userResponse] = await Promise.all([
      axios.get('/auth/me'),
      fetchVpnStatus() // Fetch VPN status in parallel using shared composable
    ])
    user.value = userResponse.data
    nameForm.first_name = user.value?.first_name || ''
    nameForm.last_name = user.value?.last_name || ''
    nameForm.organization = user.value?.organization || ''
    if (['instructor', 'admin'].includes(user.value?.role)) {
      await fetchModules()
      loadStudioLlm()
    }
  } catch (error) {
    console.error('Failed to fetch user info:', error)
  } finally {
    loading.value = false
  }
}

// Refresh VPN status every 10 seconds to match Dashboard behavior. usePoll
// pauses while the tab is hidden and refreshes immediately on return, which
// replaces the old visibilitychange handler.
//
// Returning to a hidden tab fires visibilitychange (usePoll refreshes) and
// then focus, so the focus handler skips a fetch that just ran to avoid a
// duplicate request.
let lastVpnRefresh = 0
const refreshVpnStatus = () => {
  lastVpnRefresh = Date.now()
  fetchVpnStatus()
}
const onWindowFocus = () => {
  if (Date.now() - lastVpnRefresh < 1000) return
  refreshVpnStatus()
}
usePoll(refreshVpnStatus, 10000)

onMounted(() => {
  fetchUserInfo()
  fetchSummary()
  fetchEnrolledCourses()

  // Window focus covers clicking back into the browser from another app,
  // which does not fire visibilitychange (the tab was never hidden).
  window.addEventListener('focus', onWindowFocus)
})

// Cleanup on unmount
onUnmounted(() => {
  window.removeEventListener('focus', onWindowFocus)
})

// Watch for route changes (when navigating to profile page)
watch(() => route.path, (newPath) => {
  if (newPath === '/profile') {
    // Refresh VPN status when navigating to profile page
    // Add small delay to ensure any pending VPN registrations complete
    setTimeout(() => {
      fetchVpnStatus()
    }, 500)
  }
}, { immediate: true })
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 64px);
  padding: 2rem;
  background: var(--bg-primary);
}

.profile-container {
  max-width: 1080px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2rem;
}

.loading-message {
  color: var(--text-secondary);
  text-align: center;
  padding: 2rem;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.profile-section {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.info-value {
  font-size: 1rem;
  color: var(--text-primary);
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
}

.status-badge--approved {
  background: rgba(34, 197, 94, 0.15);
  color: #10b981;
  border: 1px solid #10b981;
}

.status-badge--pending {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
  border: 1px solid var(--warning);
}

.status-badge--active {
  background: rgba(34, 197, 94, 0.15);
  color: #10b981;
  border: 1px solid #10b981;
}

.status-badge--inactive {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
  border: 1px solid var(--danger);
}

.status-badge--vpn {
  background: rgba(34, 197, 94, 0.15);
  color: #10b981;
  border: 1px solid #10b981;
}

.status-badge--no-vpn {
  background: rgba(100, 116, 139, 0.15);
  color: var(--text-muted);
  border: 1px solid var(--text-muted);
}

.status-badge--admin {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border: 1px solid #8b5cf6;
}

.status-badge--instructor {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid var(--accent);
}

.status-badge--user {
  background: rgba(148, 163, 184, 0.15);
  color: var(--text-secondary);
  border: 1px solid var(--text-secondary);
}

.name-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.name-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.name-form .form-input {
  padding-right: 1rem;
}

.certificate-preview {
  margin: 0.25rem 0 0;
}

.certificate-preview strong {
  color: var(--text-primary);
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #e2e8f0;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}

.form-input.error {
  border-color: #dc2626;
}

.form-input::placeholder {
  color: var(--text-muted);
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  transition: color 0.2s ease;
}

.password-toggle:hover {
  color: var(--text-primary);
}

.password-toggle svg {
  width: 20px;
  height: 20px;
}

.help-text {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.error-text {
  font-size: 0.8125rem;
  color: #dc2626;
  margin-top: 0.25rem;
}

.error-message {
  font-size: 0.875rem;
  color: #dc2626;
  padding: 0.75rem;
  background: rgba(220, 38, 38, 0.1);
  border-radius: 6px;
  border: 1px solid #dc2626;
}

.success-message {
  font-size: 0.875rem;
  color: #10b981;
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 6px;
  border: 1px solid #10b981;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  align-self: flex-start;
}

.btn--primary {
  background: var(--accent);
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn--primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.key-connected {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.key-connected .btn {
  align-self: auto;
}

.btn--secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn--secondary:hover {
  background: var(--nav-label);
}

.btn--ghost-danger {
  background: transparent;
  color: var(--danger);
  border: 1px solid var(--danger);
}

.btn--ghost-danger:hover {
  background: var(--danger-bg);
}

.btn--sm {
  padding: 0.3rem 0.7rem;
  font-size: 0.82rem;
}

/* LLM provider connections */
.llm-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.llm-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.6rem 0.8rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.llm-row__main {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.llm-row__label {
  font-weight: 600;
  color: var(--text-primary);
}

.llm-row__meta {
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.llm-row__url {
  font-family: monospace;
  word-break: break-all;
}

.llm-row__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.llm-add {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.08));
}

.llm-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.llm-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

/* Course Enrollment */
.join-course-form {
  margin-bottom: 1.5rem;
}

.join-row {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.join-row .form-input {
  flex: 1;
  max-width: 320px;
}

.join-row .btn {
  white-space: nowrap;
}

.enrolled-courses {
  margin-top: 1.5rem;
}

.enrolled-courses__title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

.enrolled-courses__list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.enrolled-course-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.15s;
}

.enrolled-course-card:hover {
  border-color: var(--accent);
  background: rgba(59, 130, 246, 0.05);
}

.enrolled-course-card__info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.enrolled-course-card__name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.enrolled-course-card__code {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.enrolled-course-card__arrow {
  width: 16px;
  height: 16px;
  color: var(--nav-label);
  flex-shrink: 0;
}

.empty-courses {
  color: var(--nav-label);
  font-size: 0.875rem;
  margin-top: 1rem;
}

/* ------------------------------------------------------------------ */
/* Profile hero                                                        */
/* ------------------------------------------------------------------ */

.profile-hero {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 1.75rem;
  padding: 1.75rem;
  border-radius: 18px;
  border: 1px solid var(--border-color);
  background:
    radial-gradient(circle at 8% 18%, rgba(59, 130, 246, 0.18), transparent 42%),
    radial-gradient(circle at 92% 82%, rgba(139, 92, 246, 0.14), transparent 46%),
    var(--bg-secondary);
  box-shadow: 0 18px 45px rgba(2, 6, 23, 0.18);
  overflow: hidden;
}

.profile-hero::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #f59e0b);
}

.profile-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
  width: 138px;
}

.profile-avatar__frame {
  width: 124px;
  height: 124px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border: 3px solid rgba(255, 255, 255, 0.35);
  box-shadow: 0 10px 28px rgba(30, 64, 175, 0.35);
}

.profile-avatar__frame--empty {
  background:
    linear-gradient(135deg, rgba(59, 130, 246, 0.9), rgba(139, 92, 246, 0.9));
}

.profile-avatar__frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-avatar__frame span {
  color: #fff;
  font-size: 2.25rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.avatar-input {
  display: none;
}

.profile-avatar__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.35rem;
}

.profile-avatar__actions .btn {
  align-self: auto;
}

.avatar-message {
  margin: 0;
  max-width: 180px;
  padding: 0.35rem 0.5rem;
  font-size: 0.72rem;
  text-align: center;
}

.profile-hero__identity {
  min-width: 0;
}

.profile-hero__eyebrow {
  margin: 0 0 0.35rem;
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.profile-hero__name {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.8rem, 3.5vw, 2.6rem);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.02em;
  overflow-wrap: anywhere;
}

.profile-hero__handle {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0.55rem 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  overflow-wrap: anywhere;
}

.profile-hero__dot {
  color: var(--text-muted);
}

.profile-hero__org {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.profile-hero__badges {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.9rem;
}

.profile-hero__joined {
  color: var(--text-muted);
  font-size: 0.78rem;
}

.profile-stats {
  display: flex;
  gap: 0.65rem;
}

.profile-stat {
  min-width: 86px;
  padding: 0.7rem 0.8rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: rgba(15, 23, 42, 0.22);
  text-align: center;
}

[data-theme="light"] .profile-stat {
  background: rgba(255, 255, 255, 0.72);
}

.profile-stat__value {
  display: block;
  color: var(--text-primary);
  font-size: 1.55rem;
  font-weight: 800;
  line-height: 1.15;
}

.profile-stat__value small {
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
}

.profile-stat__label {
  display: block;
  margin-top: 0.2rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

/* ------------------------------------------------------------------ */
/* Certificates and completion record                                  */
/* ------------------------------------------------------------------ */

.transcript-section {
  padding: 1.6rem;
}

.transcript-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.transcript-head .section-title {
  margin: 0 0 0.3rem;
  padding-bottom: 0;
  border-bottom: 0;
}

.transcript-help {
  margin: 0;
  max-width: 660px;
  font-size: 0.82rem;
}

.transcript-download {
  flex-shrink: 0;
  align-self: flex-start;
}

.transcript-download svg {
  width: 16px;
  height: 16px;
}

.transcript-message {
  margin-top: 1rem;
}

.certificate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(245px, 1fr));
  gap: 0.85rem;
  margin-top: 1.35rem;
}

.certificate-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 1.05rem 1rem 0.95rem;
  border-radius: 14px;
  border: 1px solid rgba(176, 141, 60, 0.35);
  background:
    linear-gradient(150deg, rgba(245, 158, 11, 0.11), transparent 58%),
    var(--bg-primary);
  color: inherit;
  text-decoration: none;
  transition: transform 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease;
}

.certificate-card:hover {
  transform: translateY(-2px);
  border-color: #b08d3c;
  box-shadow: 0 12px 26px rgba(2, 6, 23, 0.18);
}

.certificate-card__seal {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  margin-bottom: 0.3rem;
  border-radius: 50%;
  border: 1px solid rgba(176, 141, 60, 0.55);
  background: rgba(245, 158, 11, 0.12);
  color: #b08d3c;
}

.certificate-card__seal svg {
  width: 22px;
  height: 22px;
}

.certificate-card__track {
  font-size: 0.67rem;
  font-weight: 800;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.certificate-card__title {
  color: var(--text-primary);
  font-size: 0.98rem;
  font-weight: 700;
  line-height: 1.35;
}

.certificate-card__meta {
  color: var(--text-secondary);
  font-size: 0.75rem;
  line-height: 1.45;
}

.certificate-card__id {
  margin-top: 0.25rem;
  color: var(--text-muted);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.62rem;
  letter-spacing: 0.02em;
  overflow-wrap: anywhere;
}

.empty-transcript {
  margin-top: 1.25rem;
  padding: 1rem;
  border-radius: 10px;
  border: 1px dashed var(--border-color);
  color: var(--text-muted);
  font-size: 0.85rem;
}

.profile-tracks {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-color);
}

.subsection-title {
  margin: 0 0 0.75rem;
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.track-progress {
  margin-top: 0.75rem;
  padding: 0.85rem 0.95rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.track-progress__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
}

.track-progress__name {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 600;
}

.track-progress__count {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.track-progress__bar {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.track-progress__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transition: width 0.35s ease;
}

.track-progress__levels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.5rem;
  margin-top: 0.7rem;
}

.level-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.level-card--started {
  border-color: color-mix(in srgb, var(--accent) 45%, var(--border-color));
}

.level-card--complete {
  border-color: color-mix(in srgb, var(--success) 45%, var(--border-color));
  background: var(--success-bg);
}

.level-card__head,
.level-card__foot {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}

.level-card__number {
  color: var(--text-muted);
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.level-card__status {
  color: var(--text-secondary);
  font-size: 0.64rem;
  font-weight: 600;
}

.level-card--complete .level-card__status {
  color: var(--success);
}

.level-card__name {
  overflow-wrap: anywhere;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1.3;
}

.level-card__progress {
  height: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.level-card__progress span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
  transition: width 0.35s ease;
}

.level-card--complete .level-card__progress span {
  background: var(--success);
}

.level-card__foot {
  color: var(--text-muted);
  font-size: 0.66rem;
}

.level-card__cert {
  color: var(--success);
  font-weight: 700;
}

.completion-details {
  margin-top: 1.5rem;
  padding-top: 1.1rem;
  border-top: 1px solid var(--border-color);
}

.completion-details summary {
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.completion-details summary:hover {
  color: var(--accent);
}

.completion-table-wrap {
  margin-top: 0.85rem;
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.completion-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.completion-table th {
  padding: 0.55rem 0.7rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-align: left;
  text-transform: uppercase;
  white-space: nowrap;
}

.completion-table td {
  padding: 0.55rem 0.7rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  vertical-align: top;
}

.completion-table tr:last-child td {
  border-bottom: 0;
}

.completion-table__lab {
  display: block;
  color: var(--text-primary);
  font-weight: 600;
}

.completion-table__level {
  display: block;
  margin-top: 0.1rem;
  color: var(--text-muted);
  font-size: 0.7rem;
}

.achievement-strip {
  margin-top: 1.5rem;
  padding-top: 1.1rem;
  border-top: 1px solid var(--border-color);
}

.achievement-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.achievement-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.32rem 0.7rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.achievement-chip__icon {
  font-size: 0.95rem;
  line-height: 1;
}

@media (max-width: 900px) {
  .profile-hero {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .profile-stats {
    grid-column: 1 / -1;
    justify-content: stretch;
  }

  .profile-stat {
    flex: 1;
  }
}

@media (max-width: 640px) {
  .profile-page {
    padding: 1rem;
  }

  .profile-hero {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
    padding: 1.4rem 1rem;
  }

  .profile-hero__handle,
  .profile-hero__badges {
    justify-content: center;
  }

  .profile-stats {
    width: 100%;
  }

  .profile-stat {
    min-width: 0;
    padding: 0.6rem 0.4rem;
  }

  .transcript-section {
    padding: 1.1rem;
  }

  .transcript-head {
    flex-direction: column;
  }

  .transcript-download {
    width: 100%;
  }
}

.mfa-qr-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  margin: 0.6rem 0;
}

.mfa-qr {
  width: 180px;
  height: 180px;
  padding: 8px;
  border-radius: 8px;
  background: #fff;
  image-rendering: pixelated;
}

.mfa-manual {
  margin-top: 0.35rem;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.mfa-manual summary {
  cursor: pointer;
  color: var(--accent);
  font-weight: 600;
}
</style>

