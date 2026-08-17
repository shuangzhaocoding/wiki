<template>
  <div class="register-container">
    <AuthLocaleSwitcher />
    <div class="register-box">
      <h2 class="register-title">{{ translate('register.title') }}</h2>
      
      <tiny-form
        ref="registerFormRef"
        class="auth-form"
        :model="registerForm"
        :rules="rules"
        :label-position="formLabelPosition"
        :label-width="formLabelWidth"
        @submit.prevent="handleRegister"
      >
        <tiny-form-item :label="translate('register.email')" prop="email">
          <tiny-input
            v-model="registerForm.email"
            :placeholder="translate('register.email.placeholder')"
            clearable
          />
        </tiny-form-item>

        <tiny-form-item :label="translate('register.emailCode')" prop="emailCode">
          <div class="code-row">
            <tiny-input
              v-model="registerForm.emailCode"
              :placeholder="translate('register.emailCode.placeholder')"
              clearable
            />
            <tiny-button
              class="code-button"
              :disabled="codeSending || countdown > 0"
              :loading="codeSending"
              @click="handleSendCode"
            >
              {{ countdown > 0 ? translate('register.emailCode.resend', { seconds: String(countdown) }) : translate('register.emailCode.send') }}
            </tiny-button>
          </div>
        </tiny-form-item>

        <tiny-form-item :label="translate('register.password')" prop="password">
          <tiny-input
            v-model="registerForm.password"
            type="password"
            :placeholder="translate('register.password.placeholder')"
            show-password
            clearable
          />
        </tiny-form-item>

        <tiny-form-item :label="translate('register.confirmPassword')" prop="confirmPassword">
          <tiny-input
            v-model="registerForm.confirmPassword"
            type="password"
            :placeholder="translate('register.confirmPassword.placeholder')"
            show-password
            clearable
          />
        </tiny-form-item>

        <tiny-form-item>
          <tiny-button
            type="primary"
            :loading="loading"
            @click="handleRegister"
            style="width: 100%"
          >
            {{ translate('register.button') }}
          </tiny-button>
        </tiny-form-item>

        <tiny-form-item>
          <div class="register-footer">
            <span>{{ translate('register.hasAccount') }}</span>
            <router-link to="/login" class="login-link">{{ translate('register.login') }}</router-link>
          </div>
        </tiny-form-item>
      </tiny-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Form as TinyForm, FormItem as TinyFormItem, Input as TinyInput, Button as TinyButton, Modal } from '@opentiny/vue'
import { authApi, type RegisterRequest } from '../api/auth'
import { authUtils } from '../utils/auth'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
import AuthLocaleSwitcher from '../components/AuthLocaleSwitcher.vue'
import { useAuthFormLayout } from '../composables/useAuthFormLayout'

const router = useRouter()
const { formLabelPosition, formLabelWidth } = useAuthFormLayout()
const registerFormRef = ref()
const loading = ref(false)
const codeSending = ref(false)
const countdown = ref(0)
const localeStore = useLocaleStore()
let countdownTimer: ReturnType<typeof setInterval> | null = null

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const registerForm = reactive({
  email: '',
  emailCode: '',
  password: '',
  confirmPassword: ''
})

// 自定义验证：确认密码
const validateConfirmPassword = (_rule: any, value: string, callback: Function) => {
  if (value === '') {
    callback(new Error(translate('register.confirmPassword.required')))
  } else if (value !== registerForm.password) {
    callback(new Error(translate('register.confirmPassword.mismatch')))
  } else {
    callback()
  }
}

// 邮箱验证
const validateEmail = (_rule: any, value: string, callback: Function) => {
  if (!value || value === '') {
    callback(new Error(translate('register.email.required')))
    return
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) {
    callback(new Error(translate('register.email.invalid')))
  } else {
    callback()
  }
}

const validateEmailCode = (_rule: any, value: string, callback: Function) => {
  if (!value || value.trim() === '') {
    callback(new Error(translate('register.emailCode.required')))
  } else {
    callback()
  }
}

const rules = computed(() => ({
  email: [
    { required: true, validator: validateEmail, trigger: 'blur' }
  ],
  password: [
    { required: true, message: translate('register.password.required'), trigger: 'blur' },
    { min: 6, message: translate('register.password.min'), trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: translate('register.confirmPassword.required'), trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  emailCode: [
    { required: true, validator: validateEmailCode, trigger: 'blur' }
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
  const email = registerForm.email.trim()
  if (!isValidEmail(email)) {
    Modal.message({ message: translate('register.email.invalid'), status: 'warning' })
    return
  }

  codeSending.value = true
  try {
    await authApi.sendRegisterCode({ email })
    Modal.message({ message: translate('register.emailCode.sent'), status: 'success' })
    startCountdown()
  } catch (error: any) {
    // Modal.message({ message: error?.message || translate('register.emailCode.sendFailed'), status: 'error' })
  } finally {
    codeSending.value = false
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    loading.value = true
    try {
      const registerData: RegisterRequest = {
        username: registerForm.email.trim(),
        email: registerForm.email.trim(),
        email_code: registerForm.emailCode.trim(),
        password: registerForm.password
      }
      const response = await authApi.register(registerData)

      if ('access_token' in response && 'token_type' in response) {
        authUtils.setToken(response.access_token as string, response.token_type as string)
        router.push('/')
      } else {
        router.push('/login')
      }

      Modal.message({ message: translate('register.success'), status: 'success' })
    } catch (error: any) {
      const errorMsg = error?.message || translate('register.failed')
      Modal.message({ message: errorMsg, status: 'error' })
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

.register-container {
  .auth-page-shell();
}

.register-box {
  .auth-page-card(400px);
  .auth-form-responsive();
}

.register-title {
  .auth-page-title();
}

.register-footer {
  .auth-page-footer();
}

.code-row {
  .auth-code-row();
}

.login-link {
  .auth-page-link();
  margin-left: 5px;
}
</style>
