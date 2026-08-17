<template>
  <div class="forgot-password-container">
    <AuthLocaleSwitcher />
    <div class="forgot-password-box">
      <h2 class="forgot-password-title">{{ translate('forgotPassword.title') }}</h2>
      <p class="forgot-password-desc">{{ translate('forgotPassword.description') }}</p>

      <tiny-form
        ref="forgotPasswordFormRef"
        class="auth-form"
        :model="forgotPasswordForm"
        :rules="rules"
        :label-position="formLabelPosition"
        :label-width="formLabelWidth"
        @submit.prevent="handleSubmit"
      >
        <tiny-form-item :label="translate('forgotPassword.email')" prop="email">
          <tiny-input
            v-model="forgotPasswordForm.email"
            :placeholder="translate('forgotPassword.email.placeholder')"
            clearable
          />
        </tiny-form-item>

        <tiny-form-item :label="translate('forgotPassword.emailCode')" prop="emailCode">
          <div class="code-row">
            <tiny-input
              v-model="forgotPasswordForm.emailCode"
              :placeholder="translate('forgotPassword.emailCode.placeholder')"
              clearable
            />
            <tiny-button
              class="code-button"
              :disabled="codeSending || countdown > 0"
              :loading="codeSending"
              @click="handleSendCode"
            >
              {{ countdown > 0 ? translate('forgotPassword.emailCode.resend', { seconds: String(countdown) }) : translate('forgotPassword.emailCode.send') }}
            </tiny-button>
          </div>
        </tiny-form-item>

        <tiny-form-item :label="translate('forgotPassword.newPassword')" prop="newPassword">
          <tiny-input
            v-model="forgotPasswordForm.newPassword"
            type="password"
            :placeholder="translate('forgotPassword.newPassword.placeholder')"
            show-password
            clearable
          />
        </tiny-form-item>

        <tiny-form-item :label="translate('forgotPassword.confirmPassword')" prop="confirmPassword">
          <tiny-input
            v-model="forgotPasswordForm.confirmPassword"
            type="password"
            :placeholder="translate('forgotPassword.confirmPassword.placeholder')"
            show-password
            clearable
            @keyup.enter="handleSubmit"
          />
        </tiny-form-item>

        <tiny-form-item>
          <tiny-button
            type="primary"
            :loading="loading"
            @click="handleSubmit"
            style="width: 100%"
          >
            {{ translate('forgotPassword.button') }}
          </tiny-button>
        </tiny-form-item>

        <tiny-form-item>
          <div class="forgot-password-footer">
            <span>{{ translate('forgotPassword.backToLoginPrefix') }}</span>
            <router-link to="/login" class="login-link">{{ translate('forgotPassword.backToLogin') }}</router-link>
          </div>
        </tiny-form-item>
      </tiny-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Form as TinyForm, FormItem as TinyFormItem, Input as TinyInput, Button as TinyButton, Modal } from '@opentiny/vue'
import { authApi, type ResetPasswordRequest } from '../api/auth'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
import AuthLocaleSwitcher from '../components/AuthLocaleSwitcher.vue'
import { useAuthFormLayout } from '../composables/useAuthFormLayout'

const router = useRouter()
const { formLabelPosition, formLabelWidth } = useAuthFormLayout()
const localeStore = useLocaleStore()
const forgotPasswordFormRef = ref()
const loading = ref(false)
const codeSending = ref(false)
const countdown = ref(0)
let countdownTimer: ReturnType<typeof setInterval> | null = null

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const forgotPasswordForm = reactive({
  email: '',
  emailCode: '',
  newPassword: '',
  confirmPassword: ''
})

const validateEmail = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (!value) {
    callback(new Error(translate('forgotPassword.email.required')))
    return
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) {
    callback(new Error(translate('forgotPassword.email.invalid')))
    return
  }

  callback()
}

const validateEmailCode = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (!value || !value.trim()) {
    callback(new Error(translate('forgotPassword.emailCode.required')))
    return
  }

  callback()
}

const validateNewPassword = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (!value) {
    callback(new Error(translate('forgotPassword.newPassword.required')))
    return
  }

  if (value.length < 6) {
    callback(new Error(translate('forgotPassword.newPassword.min')))
    return
  }

  callback()
}

const validateConfirmPassword = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (!value) {
    callback(new Error(translate('forgotPassword.confirmPassword.required')))
    return
  }

  if (value !== forgotPasswordForm.newPassword) {
    callback(new Error(translate('forgotPassword.confirmPassword.mismatch')))
    return
  }

  callback()
}

const rules = computed(() => ({
  email: [
    { required: true, message: translate('forgotPassword.email.required'), trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ],
  emailCode: [
    { required: true, message: translate('forgotPassword.emailCode.required'), trigger: 'blur' },
    { validator: validateEmailCode, trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: translate('forgotPassword.newPassword.required'), trigger: 'blur' },
    { validator: validateNewPassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: translate('forgotPassword.confirmPassword.required'), trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}))

const isValidEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)

const startCountdown = () => {
  countdown.value = 60
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
  countdownTimer = setInterval(() => {
    if (countdown.value <= 1) {
      countdown.value = 0
      if (countdownTimer) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
      return
    }
    countdown.value -= 1
  }, 1000)
}

const handleSendCode = async () => {
  const email = forgotPasswordForm.email.trim()
  if (!isValidEmail(email)) {
    Modal.message({ message: translate('forgotPassword.email.invalid'), status: 'warning' })
    return
  }

  codeSending.value = true
  try {
    await authApi.sendResetPasswordCode({ email })
    Modal.message({ message: translate('forgotPassword.emailCode.sent'), status: 'success' })
    startCountdown()
  } catch (error: any) {
    Modal.message({
      message: error?.message || translate('forgotPassword.emailCode.sendFailed'),
      status: 'error'
    })
  } finally {
    codeSending.value = false
  }
}

const handleSubmit = async () => {
  if (!forgotPasswordFormRef.value) return

  await forgotPasswordFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    loading.value = true
    try {
      const payload: ResetPasswordRequest = {
        email: forgotPasswordForm.email.trim(),
        email_code: forgotPasswordForm.emailCode.trim(),
        new_password: forgotPasswordForm.newPassword
      }
      await authApi.resetPassword(payload)
      Modal.message({
        message: translate('forgotPassword.success'),
        status: 'success'
      })
      router.push('/login')
    } catch (error: any) {
      Modal.message({
        message: error?.message || translate('forgotPassword.failed'),
        status: 'error'
      })
    } finally {
      loading.value = false
    }
  })
}

onBeforeUnmount(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped lang="less">
@import '../styles/auth-page-shell.less';

.forgot-password-container {
  .auth-page-shell();
}

.forgot-password-box {
  .auth-page-card(420px);
  .auth-form-responsive();
}

.forgot-password-title {
  .auth-page-title();
  margin-bottom: 12px;
}

.forgot-password-desc {
  .auth-page-desc();
}

.code-row {
  .auth-code-row();
}

.forgot-password-footer {
  .auth-page-footer();
}

.login-link {
  .auth-page-link();
  margin-left: 5px;
}
</style>
